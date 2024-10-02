from typing import TypedDict, List, Dict

from webviz_subsurface._utils.enum_shim import StrEnum


class MapAttribute(StrEnum):
    MIGRATION_TIME_SGAS = "Migration time (SGAS)"
    MIGRATION_TIME_AMFG = "Migration time (AMFG)"
    MAX_SGAS = "Maximum SGAS"
    MAX_AMFG = "Maximum AMFG"
    SGAS_PLUME = "Plume (SGAS)"
    AMFG_PLUME = "Plume (AMFG)"
    MASS = "Mass"
    DISSOLVED = "Dissolved mass"
    FREE = "Free mass"


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
    VISUALIZATION_THRESHOLDS = "Manage visualization filter"


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


class MapThresholds:
    _standard_thresholds = {}

    def __init__(self, mapping: Dict[str, str]):
        self.set_map_thresholds(mapping)

    def get_standard_thresholds(self):
        return self._standard_thresholds

    def set_map_thresholds(self, mapping):
        self._standard_thresholds["" + MapAttribute.MAX_SGAS] = 0
        self._standard_thresholds["" + MapAttribute.MAX_AMFG] = 0.0005
        self._standard_thresholds["" + MapAttribute.MASS] = 0
        self._standard_thresholds["" + MapAttribute.DISSOLVED] = 0
        self._standard_thresholds["" + MapAttribute.FREE] = 0

        for key in mapping.keys():
            if key not in MapAttribute:
                self._standard_thresholds[key] = 0

    def get_keys(self):
        return list(self._standard_thresholds.keys())
