import glob
import logging
import os
import warnings
from pathlib import Path
from typing import Dict, List, Optional

from webviz_config import WebvizSettings

from webviz_subsurface._providers import (
    EnsembleSurfaceProvider,
    EnsembleSurfaceProviderFactory,
    EnsembleTableProvider,
    EnsembleTableProviderFactory,
)
from webviz_subsurface._utils.webvizstore_functions import read_csv
from webviz_subsurface.plugins._co2_leakage._utilities.containment_data_provider import (
    ContainmentDataProvider
)
from webviz_subsurface.plugins._co2_leakage._utilities.generic import (
    GraphSource,
    MapAttribute,
    MapNamingConvention,
    FilteredMapAttribute,
    MenuOptions,
)
from webviz_subsurface.plugins._co2_leakage._utilities.unsmry_data_provider import (
    UnsmryDataProvider
)
from webviz_subsurface.plugins._map_viewer_fmu._tmp_well_pick_provider import (
    WellPickProvider,
)
from webviz_subsurface._providers.ensemble_surface_provider._surface_discovery import (
    discover_per_realization_surface_files,
)

LOGGER = logging.getLogger(__name__)
WARNING_THRESHOLD_CSV_FILE_SIZE_MB = 100.0


def build_mapping(
        webviz_settings: WebvizSettings,
        ensembles: List[str],
) -> Dict[MapAttribute, str]:
    available_attrs_per_ensemble = [discover_per_realization_surface_files(
        webviz_settings.shared_settings["scratch_ensembles"][ens],
        "share/results/maps"
    ) for ens in ensembles]
    full_attr_list = [[attr.attribute for attr in ens]
                      for ens in available_attrs_per_ensemble]
    unique_attributes = set()
    for ens_attr in full_attr_list:
        unique_attributes.update(ens_attr)
    unique_attributes = list(unique_attributes)
    mapping = {}
    for attr in unique_attributes:
        for name_convention in MapNamingConvention:
            if attr == name_convention.value:
                attribute_key = MapAttribute[name_convention.name].name
                mapping[attribute_key] = attr
                break
    return mapping


def init_map_attribute_names(
    webviz_settings: WebvizSettings,
    ensembles: List[str],
    mapping: Optional[Dict[str, str]]
) -> Dict[MapAttribute, str]:
    if mapping is None:
        # Based on name convention of xtgeoapp_grd3dmaps:
        mapping = build_mapping(webviz_settings,ensembles)
    final_attributes = {(MapAttribute[key].value if key in MapAttribute.__members__ else key):
                        value for key, value in mapping.items()}
    return FilteredMapAttribute(final_attributes)


def init_surface_providers(
    webviz_settings: WebvizSettings,
    ensembles: List[str],
) -> Dict[str, EnsembleSurfaceProvider]:
    surface_provider_factory = EnsembleSurfaceProviderFactory.instance()
    return {
        ens: surface_provider_factory.create_from_ensemble_surface_files(
            webviz_settings.shared_settings["scratch_ensembles"][ens],
        )
        for ens in ensembles
    }


def init_well_pick_provider(
    well_pick_dict: Dict[str, Optional[str]],
    map_surface_names_to_well_pick_names: Optional[Dict[str, str]],
) -> Dict[str, Optional[WellPickProvider]]:
    well_pick_provider: Dict[str, Optional[WellPickProvider]] = {}
    ensembles = list(well_pick_dict.keys())
    for ens in ensembles:
        well_pick_path = well_pick_dict[ens]
        if well_pick_path is None:
            well_pick_provider[ens] = None
        else:
            try:
                well_pick_provider[ens] = WellPickProvider(
                    read_csv(well_pick_path), map_surface_names_to_well_pick_names
                )
            except OSError:
                well_pick_provider[ens] = None
    return well_pick_provider


def init_unsmry_data_providers(
    ensemble_roots: Dict[str, str],
    table_rel_path: Optional[str],
) -> Dict[str, UnsmryDataProvider]:
    if table_rel_path is None:
        return {}
    factory = EnsembleTableProviderFactory.instance()
    providers = {
        ens: _init_ensemble_table_provider(factory, ens, ens_path, table_rel_path)
        for ens, ens_path in ensemble_roots.items()
    }
    return {
        k: UnsmryDataProvider(v)
        for k, v in providers.items()
        if v is not None
    }


def init_containment_data_providers(
    ensemble_roots: Dict[str, str],
    table_rel_path: str,
) -> Dict[str, ContainmentDataProvider]:
    factory = EnsembleTableProviderFactory.instance()
    providers = {
        ens: _init_ensemble_table_provider(factory, ens, ens_path, table_rel_path)
        for ens, ens_path in ensemble_roots.items()
    }
    return {
        k: ContainmentDataProvider(v)
        for k, v in providers.items()
        if v is not None
    }


def _init_ensemble_table_provider(
    factory: EnsembleTableProviderFactory,
    ens: str,
    ens_path: str,
    table_rel_path: str,
) -> Optional[EnsembleTableProvider]:
    try:
        return factory.create_from_per_realization_arrow_file(
            ens_path, table_rel_path
        )
    except (KeyError, ValueError) as exc:
        try:
            return factory.create_from_per_realization_csv_file(
                ens_path, table_rel_path
            )
        except (KeyError, ValueError) as exc2:
            LOGGER.warning(
                f'Tried reading "{table_rel_path}" for ensemble "{ens}" as csv with'
                f' error {exc}, and as arrow with error {exc2}'
            )
    return None


def init_menu_options(
    ensemble_roots: Dict[str, str],
    mass_table: Dict[str, ContainmentDataProvider],
    actual_volume_table: Dict[str, ContainmentDataProvider],
    unsmry_providers: Dict[str, UnsmryDataProvider],
) -> Dict[str, Dict[GraphSource, MenuOptions]]:
    options: Dict[str, Dict[GraphSource, MenuOptions]] = {}
    for ens in ensemble_roots.keys():
        options[ens] = {
            GraphSource.CONTAINMENT_MASS: mass_table[ens].menu_options,
            GraphSource.CONTAINMENT_ACTUAL_VOLUME: actual_volume_table[ens].menu_options,
        }
        if ens in unsmry_providers:
            options[ens][GraphSource.UNSMRY] = unsmry_providers[ens].menu_options
    return options


def process_files(
    cont_bound: Optional[str],
    haz_bound: Optional[str],
    well_file: Optional[str],
    ensemble_paths: Dict[str, str],
) -> List[Dict[str, Optional[str]]]:
    """
    Checks if the files exist (otherwise gives a warning and returns None)
    Concatenates ensemble root dir and path to file if relative
    """
    ensembles = list(ensemble_paths.keys())
    return [
        {ens: _process_file(source, ensemble_paths[ens]) for ens in ensembles}
        for source in [cont_bound, haz_bound, well_file]
    ]


def _process_file(file: Optional[str], ensemble_path: str) -> Optional[str]:
    if file is not None:
        if Path(file).is_absolute():
            if os.path.isfile(Path(file)):
                return file
            warnings.warn(f"Cannot find specified file {file}.")
            return None
        file = os.path.join(Path(ensemble_path).parents[1], file)
        if not os.path.isfile(file):
            warnings.warn(
                f"Cannot find specified file {file}.\n"
                "Note that relative paths are accepted from ensemble root "
                "(directory with the realizations)."
            )
            return None
    return file
