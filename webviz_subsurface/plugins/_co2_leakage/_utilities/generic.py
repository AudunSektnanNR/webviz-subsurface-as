from __future__ import (  # Change to import Self from typing if we update to Python >3.11
    annotations,
)

from typing import Dict, List, TypedDict

from webviz_subsurface._utils.enum_shim import StrEnum


class MapAttribute(StrEnum):
    MIGRATION_TIME_GAS_PHASE = "Migration time (gas)"
    MIGRATION_TIME_DISSOLVED_PHASE = "Migration time (dissolved)"
    MAX_GAS_PHASE = "Maximum gas"
    MAX_DISSOLVED_PHASE = "Maximum dissolved"
    MAX_TRAPPED_PHASE = "Maximum trapped gas"
    GAS_PHASE_PLUME = "Plume (gas_phase)"
    DISSOLVED_PHASE_PLUME = "Plume (dissolved_phase)"
    TRAPPED_PHASE_PLUME = "Plume (trapped_phase)"
    MASS = "Mass"
    DISSOLVED = "Dissolved mass"
    FREE = "Free gas mass"
    FREE_GAS = "Free gas phase mass"
    TRAPPED_GAS = "Trapped gas phase mass"


class MapGroup(StrEnum):
    MIGRATION_TIME_GAS_PHASE = "gas_phase"
    MIGRATION_TIME_DISSOLVED_PHASE = "dissolved_phase"
    MAX_GAS_PHASE = "gas_phase"
    MAX_DISSOLVED_PHASE = "dissolved_phase"
    MAX_TRAPPED_PHASE = "trapped_phase"
    GAS_PHASE_PLUME = "gas_phase"
    DISSOLVED_PHASE_PLUME = "dissolved_phase"
    TRAPPED_PHASE_PLUME = "trapped_phase"
    MASS = "CO2 MASS"
    DISSOLVED = "CO2 MASS"
    FREE = "CO2 MASS"
    FREE_GAS = "CO2 MASS"
    TRAPPED_GAS = "CO2 MASS"


class MapType(StrEnum):
    MIGRATION_TIME_GAS_PHASE = "MIGRATION_TIME"
    MIGRATION_TIME_DISSOLVED_PHASE = "MIGRATION_TIME"
    MAX_GAS_PHASE = "MAX"
    MAX_DISSOLVED_PHASE = "MAX"
    MAX_TRAPPED_PHASE = "MAX"
    GAS_PHASE_PLUME = "PLUME"
    DISSOLVED_PHASE_PLUME = "PLUME"
    TRAPPED_PHASE_PLUME = "PLUME"
    MASS = "MASS"
    DISSOLVED = "MASS"
    FREE = "MASS"
    FREE_GAS = "MASS"
    TRAPPED_GAS = "MASS"


class MapNamingConvention(StrEnum):
    MIGRATION_TIME_GAS_PHASE = "migrationtime_gas_phase"
    MIGRATION_TIME_DISSOLVED_PHASE = "migrationtime_dissolved_phase"
    MAX_GAS_PHASE = "max_gas_phase"
    MAX_DISSOLVED_PHASE = "max_dissolved_phase"
    MAX_TRAPPED_PHASE = "max_trapped_phase"
    MASS = "co2_mass_total"
    DISSOLVED = "co2_mass_dissolved_phase"
    FREE = "co2_mass_gas_phase"
    FREE_GAS = "co2_mass_free_gas_phase"
    TRAPPED_GAS = "co2_mass_trapped_gas_phase"


class FilteredMapAttribute:
    def __init__(self, mapping: Dict):
        self.mapping = mapping
        map_types = {
            key: MapType[key].value
            for key in MapAttribute.__members__
            if MapAttribute[key].value in self.mapping
        }
        map_groups = {
            key: MapGroup[key].value
            for key in MapAttribute.__members__
            if MapAttribute[key].value in self.mapping
        }
        map_attrs_with_plume = [
            map_groups[key] for key, value in map_types.items() if value == "MAX"
        ]
        plume_request = {
            f"Plume ({item})": f"{item.lower()}_plume" for item in map_attrs_with_plume
        }
        self.mapping.update(plume_request)
        self.filtered_values = self.filter_map_attribute()

    def filter_map_attribute(self) -> Dict:
        return {
            MapAttribute[key]: self.mapping[MapAttribute[key].value]
            for key in MapAttribute.__members__
            if MapAttribute[key].value in self.mapping
        }

    def __getitem__(self, key: MapAttribute) -> MapAttribute:
        if isinstance(key, MapAttribute):
            return self.filtered_values[key]
        raise KeyError(f"Key must be a MapAttribute, " f"got {type(key)} instead.")

    @property
    def values(self) -> Dict:
        return self.filtered_values


class Co2MassScale(StrEnum):
    NORMALIZE = "Fraction"
    KG = "kg"
    TONS = "tons"
    MTONS = "M tons"


class Co2VolumeScale(StrEnum):
    NORMALIZE = "Fraction"
    BILLION_CUBIC_METERS = "Cubic kms"
    CUBIC_METERS = "Cubic meters"


class GraphSource(StrEnum):
    UNSMRY = "UNSMRY"
    CONTAINMENT_MASS = "Containment Data (mass)"
    CONTAINMENT_ACTUAL_VOLUME = "Containment Data (volume, actual)"


class LayoutLabels(StrEnum):
    """Text labels used in layout components"""

    SHOW_FAULTPOLYGONS = "Show fault polygons"
    SHOW_CONTAINMENT_POLYGON = "Show containment polygon"
    SHOW_HAZARDOUS_POLYGON = "Show hazardous polygon"
    SHOW_WELLS = "Show wells"
    WELL_FILTER = "Well filter"
    COMMON_SELECTIONS = "Options and global filters"
    FEEDBACK = "User feedback"
    VISUALIZATION_UPDATE = "Update threshold"
    VISUALIZATION_THRESHOLDS = "Manage visualization filter"
    ALL_REAL = "Select all"


# pylint: disable=too-few-public-methods
class LayoutStyle:
    """CSS styling"""

    OPTIONS_BUTTON = {
        "marginBottom": "10px",
        "width": "100%",
        "height": "30px",
        "line-height": "30px",
        "background-color": "lightgrey",
    }

    ALL_REAL_BUTTON = {
        "marginLeft": "10px",
        "height": "25px",
        "line-height": "25px",
        "background-color": "lightgrey",
    }

    FEEDBACK_BUTTON = {
        "marginBottom": "10px",
        "width": "100%",
        "height": "30px",
        "line-height": "30px",
        "background-color": "lightgrey",
    }

    VISUALIZATION_BUTTON = {
        "marginLeft": "10px",
        "height": "30px",
        "line-height": "30px",
        "background-color": "lightgrey",
    }

    THRESHOLDS_BUTTON = {
        "marginTop": "10px",
        "width": "100%",
        "height": "30px",
        "line-height": "30px",
        "padding": "0",
        "background-color": "lightgrey",
    }


class MenuOptions(TypedDict):
    zones: List[str]
    regions: List[str]
    phases: List[str]
    plume_groups: List[str]


class MapThresholds:
    def __init__(self, mapping: FilteredMapAttribute):
        self.standard_thresholds = {
            MapAttribute[key.name].value: 0.0
            for key in mapping.filtered_values.keys()
            if MapType[MapAttribute[key.name].name].value
            not in ["PLUME", "MIGRATION_TIME"]
        }
        if MapAttribute.MAX_DISSOLVED_PHASE in self.standard_thresholds.keys():
            self.standard_thresholds[MapAttribute.MAX_DISSOLVED_PHASE] = 0.0005
