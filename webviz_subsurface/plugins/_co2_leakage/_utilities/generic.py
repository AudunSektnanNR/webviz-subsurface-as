from typing import TypedDict, List

from webviz_subsurface._utils.enum_shim import StrEnum


class MapAttribute(StrEnum):
    MIGRATION_TIME_SGAS = "Migration time (SGAS)"
    MIGRATION_TIME_AMFG = "Migration time (AMFG)"
    MAX_SGAS = "Maximum SGAS"
    MAX_AMFG = "Maximum AMFG"
    MAX_SGSTRAND = "Maximum SGSTRAND"
    SGAS_PLUME = "Plume (SGAS)"
    AMFG_PLUME = "Plume (AMFG)"
    SGSTRAND_PLUME = "Plume (SGSTRAND)"
    MASS = "Mass"
    DISSOLVED = "Dissolved mass"
    FREE = "Free mass"
    FREE_GAS = "Free gas phase mass"
    TRAPPED_GAS = "Trapped gas phase mass"


class MapGroup(StrEnum):
    MIGRATION_TIME_SGAS = "SGAS"
    MIGRATION_TIME_AMFG = "AMFG"
    MAX_SGAS = "SGAS"
    MAX_AMFG = "AMFG"
    MAX_SGSTRAND = "SGSTRAND"
    SGAS_PLUME = "SGAS"
    AMFG_PLUME = "AMFG"
    SGSTRAND_PLUME = "SGSTRAND"
    MASS = "CO2 MASS"
    DISSOLVED = "CO2 MASS"
    FREE = "CO2 MASS"
    FREE_GAS = "CO2 MASS"
    TRAPPED_GAS = "CO2 MASS"


class MapType(StrEnum):
    MIGRATION_TIME_SGAS = "MIGRATION_TIME"
    MIGRATION_TIME_AMFG = "MIGRATION_TIME"
    MAX_SGAS = "MAX"
    MAX_AMFG = "MAX"
    MAX_SGSTRAND = "MAX"
    SGAS_PLUME = "PLUME"
    AMFG_PLUME = "PLUME"
    SGSTRAND_PLUME = "PLUME"
    MASS = "MASS"
    DISSOLVED = "MASS"
    FREE = "MASS"
    FREE_GAS = "MASS"
    TRAPPED_GAS = "MASS"


class MapNamingConvention(StrEnum):
    MIGRATION_TIME_SGAS = "migrationtime_sgas"
    MIGRATION_TIME_AMFG = "migrationtime_amfg"
    MAX_SGAS = "max_sgas"
    MAX_AMFG = "max_amfg"
    MAX_SGSTRAND = "max_sgstrand"
    MASS = "co2_mass_total"
    DISSOLVED = "co2_mass_aqu_phase"
    FREE = "co2_mass_gas_phase"
    FREE_GAS = "co2_mass_free_gas_phase"
    TRAPPED_GAS = "co2_mass_trapped_gas_phase"


class FilteredMapAttribute:
    def __init__(self, mapping):
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

    def filter_map_attribute(self):
        return {
            MapAttribute[key]: self.mapping[MapAttribute[key].value]
            for key in MapAttribute.__members__
            if MapAttribute[key].value in self.mapping
        }

    def __getitem__(self, key):
        if isinstance(key, MapAttribute):
            return self.filtered_values[key]
        else:
            raise KeyError(f"Key must be a MapAttribute, " f"got {type(key)} instead.")

    @property
    def values(self):
        return self.filtered_values


class Co2MassScale(StrEnum):
    NORMALIZE = "Fraction"
    MTONS = "M tons"
    KG = "Kg"


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


class MenuOptions(TypedDict):
    zones: List[str]
    regions: List[str]
    phases: List[str]
