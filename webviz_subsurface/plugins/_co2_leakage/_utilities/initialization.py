import logging
import os
from pathlib import Path
from glob import glob
from typing import Dict, List, Optional
import warnings

from webviz_config import WebvizSettings

from webviz_subsurface._providers import (
    EnsembleSurfaceProvider,
    EnsembleSurfaceProviderFactory,
    EnsembleTableProvider,
    EnsembleTableProviderFactory,
)
from webviz_subsurface._utils.webvizstore_functions import read_csv
from webviz_subsurface.plugins._co2_leakage._utilities.generic import MapAttribute
from webviz_subsurface.plugins._map_viewer_fmu._tmp_well_pick_provider import (
    WellPickProvider,
)

LOGGER = logging.getLogger(__name__)


def init_map_attribute_names(
    mapping: Optional[Dict[str, str]]
) -> Dict[MapAttribute, str]:
    if mapping is None:
        # Based on name convention of xtgeoapp_grd3dmaps:
        return {
            MapAttribute.MIGRATION_TIME: "migrationtime",
            MapAttribute.MAX_SGAS: "max_sgas",
            MapAttribute.MAX_AMFG: "max_amfg",
            # MapAttribute.MASS: "mass_total",  # NBNB-AS: Or sum_mass_total
            MapAttribute.MASS: "mass",
            MapAttribute.DISSOLVED: "dissolved_mass",
            MapAttribute.FREE: "free_mass",
        }
    return {MapAttribute[key]: value for key, value in mapping.items()}


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
    well_pick_path: Optional[str],
    map_surface_names_to_well_pick_names: Optional[Dict[str, str]],
) -> Optional[WellPickProvider]:
    if well_pick_path is None:
        return None
    try:
        return WellPickProvider(
            read_csv(well_pick_path), map_surface_names_to_well_pick_names
        )
    except OSError:
        return None


def init_table_provider(
    ensemble_roots: Dict[str, str],
    table_rel_path: str,
) -> Dict[str, EnsembleTableProvider]:
    providers = {}
    factory = EnsembleTableProviderFactory.instance()
    for ens, ens_path in ensemble_roots.items():
        try:
            providers[ens] = factory.create_from_per_realization_csv_file(
                ens_path, table_rel_path
            )
        except (KeyError, ValueError) as exc:
            LOGGER.warning(
                f'Did not load "{table_rel_path}" for ensemble "{ens}" with error {exc}'
            )
    return providers


def append_if_relative(
    cont_bound: Optional[str],
    haz_bound: Optional[str],
    well_file: Optional[str],
    ens_path: str
) -> List[str]:
    if cont_bound is not None and not Path(cont_bound).is_absolute():
        cont_bound = glob(f"{Path(ens_path).parents[1]}/**/{cont_bound}", recursive=True)[0]
    if haz_bound is not None and not Path(haz_bound).is_absolute():
        haz_bound = glob(f"{Path(ens_path).parents[1]}/**/{haz_bound}", recursive=True)[0]
    if well_file is not None and not Path(well_file).is_absolute():
        well_file = glob(f"{Path(ens_path).parents[1]}/**/{well_file}", recursive=True)[0]
    return cont_bound, haz_bound, well_file


def check_if_files_exist(
    file_containment_boundary: Optional[str],
    file_hazardous_boundary: Optional[str],
    well_pick_file: Optional[str],
) -> None:
    if file_containment_boundary is not None:
        if not os.path.isfile(file_containment_boundary):
            warnings.warn(f"Cannot find specified file {file_containment_boundary}.")
    if file_hazardous_boundary is not None:
        if not os.path.isfile(file_hazardous_boundary):
            warnings.warn(f"Cannot find specified file {file_hazardous_boundary}.")
    if well_pick_file is not None:
        if not os.path.isfile(well_pick_file):
            warnings.warn(f"Cannot find specified file {well_pick_file}.")
