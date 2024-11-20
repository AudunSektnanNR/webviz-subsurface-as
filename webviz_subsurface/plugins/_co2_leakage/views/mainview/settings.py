# pylint: disable=too-many-lines
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import webviz_core_components as wcc
from dash import Input, Output, State, callback, dcc, html, no_update
from dash.development.base_component import Component
from webviz_config.utils import StrEnum
from webviz_config.webviz_plugin_subclasses import SettingsGroupABC

from webviz_subsurface._providers.ensemble_surface_provider.ensemble_surface_provider import (
    EnsembleSurfaceProvider,
    SurfaceStatistic,
)
from webviz_subsurface.plugins._co2_leakage._utilities.callbacks import property_origin
from webviz_subsurface.plugins._co2_leakage._utilities.generic import (
    Co2MassScale,
    Co2VolumeScale,
    FilteredMapAttribute,
    GraphSource,
    LayoutLabels,
    LayoutStyle,
    MapAttribute,
    MapGroup,
    MapThresholds,
    MapType,
    MenuOptions,
)


class ViewSettings(SettingsGroupABC):
    class Ids(StrEnum):
        OPTIONS_DIALOG_BUTTON = "options-dialog-button"
        OPTIONS_DIALOG = "options-dialog"
        OPTIONS_DIALOG_OPTIONS = "options-dialog-options"
        OPTIONS_DIALOG_WELL_FILTER = "options-dialog-well-filter"
        WELL_FILTER_HEADER = "well-filter-header"

        FORMATION = "formation"
        ENSEMBLE = "ensemble"
        REALIZATION = "realization"

        PROPERTY = "property"
        STATISTIC = "statistic"
        COLOR_SCALE = "color-scale"
        CM_MIN = "cm-min"
        CM_MAX = "cm-max"
        CM_MIN_AUTO = "cm-min-auto"
        CM_MAX_AUTO = "cm-max-auto"

        GRAPH_SOURCE = "graph-source"
        CO2_SCALE = "co2-scale"
        Y_MIN_GRAPH = "y-min-graph"
        Y_MAX_GRAPH = "y-max-graph"
        Y_MIN_AUTO_GRAPH = "y-min-auto-graph"
        Y_MAX_AUTO_GRAPH = "y-max-auto-graph"
        COLOR_BY = "color-by"
        MARK_BY = "mark-by"
        SORT_PLOT = "sort-plot"
        ZONE = "zone"
        ZONE_COL = "zone-column"
        REGION_COL = "region-column"
        ZONE_REGION = "zone-and-region"
        REGION = "region"
        PHASE = "phase"
        PHASE_MENU = "phase-menu"
        CONTAINMENT = "containment"
        PLUME_GROUP = "plume-group"
        CONTAINMENT_MENU = "containment-menu"
        PLUME_GROUP_MENU = "plume-group-menu"

        PLUME_THRESHOLD = "plume-threshold"
        PLUME_SMOOTHING = "plume-smoothing"

        VISUALIZATION_UPDATE = "visualization-update"
        VISUALIZATION_THRESHOLD_BUTTON = "visualization-threshold-button"
        VISUALIZATION_THRESHOLD_DIALOG = "visualization-threshold-dialog"
        MASS_UNIT = "mass-unit"
        MASS_UNIT_UPDATE = "mass-unit-update"

        FEEDBACK_BUTTON = "feedback-button"
        FEEDBACK = "feedback"

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        ensemble_paths: Dict[str, str],
        realizations_per_ensemble: Dict[str, List[int]],
        ensemble_surface_providers: Dict[str, EnsembleSurfaceProvider],
        initial_surface: Optional[str],
        map_attribute_names: FilteredMapAttribute,
        map_thresholds: MapThresholds,
        color_scale_names: List[str],
        well_names_dict: Dict[str, List[str]],
        menu_options: Dict[str, Dict[GraphSource, MenuOptions]],
        content: Dict[str, bool],
    ):
        super().__init__("Settings")
        self._ensemble_paths = ensemble_paths
        self._realizations_per_ensemble = realizations_per_ensemble
        self._ensemble_surface_providers = ensemble_surface_providers
        self._map_attribute_names = map_attribute_names
        self._thresholds = map_thresholds
        self._threshold_ids = list(self._thresholds.standard_thresholds.keys())
        self._color_scale_names = color_scale_names
        self._initial_surface = initial_surface
        self._well_names_dict = well_names_dict
        self._menu_options = menu_options
        self._content = content

    def layout(self) -> List[Component]:
        menu_layout = []
        if self._content["maps"]:
            menu_layout += [
                DialogLayout(self._well_names_dict, list(self._ensemble_paths.keys())),
                OpenDialogButton(),
            ]
        menu_layout.append(
            EnsembleSelectorLayout(
                self.register_component_unique_id(self.Ids.ENSEMBLE),
                self.register_component_unique_id(self.Ids.REALIZATION),
                list(self._ensemble_paths.keys()),
            )
        )
        if self._content["maps"]:
            menu_layout += [
                FilterSelectorLayout(
                    self.register_component_unique_id(self.Ids.FORMATION)
                ),
                VisualizationThresholdsLayout(
                    self._threshold_ids,
                    self._thresholds,
                    self.register_component_unique_id(self.Ids.VISUALIZATION_UPDATE),
                ),
                MapSelectorLayout(
                    self._color_scale_names,
                    self.register_component_unique_id(self.Ids.PROPERTY),
                    self.register_component_unique_id(self.Ids.STATISTIC),
                    self.register_component_unique_id(self.Ids.COLOR_SCALE),
                    self.register_component_unique_id(self.Ids.CM_MIN),
                    self.register_component_unique_id(self.Ids.CM_MAX),
                    self.register_component_unique_id(self.Ids.CM_MIN_AUTO),
                    self.register_component_unique_id(self.Ids.CM_MAX_AUTO),
                    self.register_component_unique_id(self.Ids.MASS_UNIT),
                    self.register_component_unique_id(self.Ids.MASS_UNIT_UPDATE),
                    self._map_attribute_names,
                ),
            ]
        if self._content["any_table"]:
            menu_layout.append(
                GraphSelectorsLayout(
                    self.register_component_unique_id(self.Ids.GRAPH_SOURCE),
                    self.register_component_unique_id(self.Ids.CO2_SCALE),
                    [
                        self.register_component_unique_id(self.Ids.Y_MIN_GRAPH),
                        self.register_component_unique_id(self.Ids.Y_MIN_AUTO_GRAPH),
                    ],
                    [
                        self.register_component_unique_id(self.Ids.Y_MAX_GRAPH),
                        self.register_component_unique_id(self.Ids.Y_MAX_AUTO_GRAPH),
                    ],
                    [
                        self.register_component_unique_id(self.Ids.COLOR_BY),
                        self.register_component_unique_id(self.Ids.MARK_BY),
                        self.register_component_unique_id(self.Ids.SORT_PLOT),
                        self.register_component_unique_id(self.Ids.ZONE),
                        self.register_component_unique_id(self.Ids.ZONE_COL),
                        self.register_component_unique_id(self.Ids.REGION),
                        self.register_component_unique_id(self.Ids.REGION_COL),
                        self.register_component_unique_id(self.Ids.ZONE_REGION),
                        self.register_component_unique_id(self.Ids.PHASE),
                        self.register_component_unique_id(self.Ids.PHASE_MENU),
                        self.register_component_unique_id(self.Ids.CONTAINMENT),
                        self.register_component_unique_id(self.Ids.CONTAINMENT_MENU),
                        self.register_component_unique_id(self.Ids.PLUME_GROUP),
                        self.register_component_unique_id(self.Ids.PLUME_GROUP_MENU),
                    ],
                    self._content,
                )
            )
        if self._content["maps"]:
            menu_layout.append(
                ExperimentalFeaturesLayout(
                    self.register_component_unique_id(self.Ids.PLUME_THRESHOLD),
                    self.register_component_unique_id(self.Ids.PLUME_SMOOTHING),
                ),
            )
        menu_layout += [
            FeedbackLayout(),
            FeedbackButton(),
        ]
        return menu_layout

    def set_callbacks(self) -> None:
        @callback(
            Output(
                self.component_unique_id(self.Ids.REALIZATION).to_string(), "options"
            ),
            Output(self.component_unique_id(self.Ids.REALIZATION).to_string(), "value"),
            Input(self.component_unique_id(self.Ids.ENSEMBLE).to_string(), "value"),
        )
        def set_realizations(ensemble: str) -> Tuple[List[Dict[str, Any]], List[int]]:
            rlz = [
                {"value": r, "label": str(r)}
                for r in self._realizations_per_ensemble[ensemble]
            ]
            return rlz, [rlz[0]["value"]]  # type: ignore

        @callback(
            Output(self.component_unique_id(self.Ids.FORMATION).to_string(), "options"),
            Output(self.component_unique_id(self.Ids.FORMATION).to_string(), "value"),
            Input(self.component_unique_id(self.Ids.PROPERTY).to_string(), "value"),
            State(self.component_unique_id(self.Ids.ENSEMBLE).to_string(), "value"),
            State(self.component_unique_id(self.Ids.FORMATION).to_string(), "value"),
        )
        def set_formations(
            prop: str, ensemble: str, current_value: str
        ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
            if ensemble is None:
                return [], None
            surface_provider = self._ensemble_surface_providers[ensemble]
            # Map
            prop_name = property_origin(MapAttribute(prop), self._map_attribute_names)
            surfaces = surface_provider.surface_names_for_attribute(prop_name)
            if len(surfaces) == 0:
                warning = f"Surface not found for property: {prop}.\n"
                warning += f"Expected name: <formation>--{prop_name}"
                if MapType[MapAttribute(prop).name].value != "MIGRATION_TIME":
                    warning += "--<date>"
                warnings.warn(warning + ".gri")
            # Formation names
            formations = [{"label": v.title(), "value": v} for v in surfaces]
            picked_formation = None
            if len(formations) != 0:
                if current_value is None and self._initial_surface in surfaces:
                    picked_formation = self._initial_surface
                elif current_value in surfaces:
                    picked_formation = no_update
                else:
                    picked_formation = (
                        "all"
                        if any((x["value"] == "all" for x in formations))
                        else formations[0]["value"]
                    )
            return formations, picked_formation

        if self._content["maps"]:

            @callback(
                Output(
                    self.component_unique_id(self.Ids.STATISTIC).to_string(), "disabled"
                ),
                Input(
                    self.component_unique_id(self.Ids.REALIZATION).to_string(), "value"
                ),
                Input(self.component_unique_id(self.Ids.PROPERTY).to_string(), "value"),
            )
            def toggle_statistics(realizations: List[int], attribute: str) -> bool:
                if len(realizations) <= 1:
                    return True
                if MapType[MapAttribute(attribute).name].value == "PLUME":
                    return True
                return False

            @callback(
                Output(
                    self.component_unique_id(self.Ids.CM_MIN).to_string(), "disabled"
                ),
                Output(
                    self.component_unique_id(self.Ids.CM_MAX).to_string(), "disabled"
                ),
                Input(
                    self.component_unique_id(self.Ids.CM_MIN_AUTO).to_string(), "value"
                ),
                Input(
                    self.component_unique_id(self.Ids.CM_MAX_AUTO).to_string(), "value"
                ),
            )
            def set_color_range_data(
                min_auto: List[str], max_auto: List[str]
            ) -> Tuple[bool, bool]:
                return len(min_auto) == 1, len(max_auto) == 1

            @callback(
                Output(
                    self.component_unique_id(self.Ids.MASS_UNIT).to_string(), "disabled"
                ),
                Input(self.component_unique_id(self.Ids.PROPERTY).to_string(), "value"),
            )
            def toggle_unit(attribute: str) -> bool:
                if MapType[MapAttribute(attribute).name].value != "MASS":
                    return True
                return False

        if self._content["any_table"]:

            @callback(
                Output(
                    self.component_unique_id(self.Ids.Y_MIN_GRAPH).to_string(),
                    "disabled",
                ),
                Output(
                    self.component_unique_id(self.Ids.Y_MAX_GRAPH).to_string(),
                    "disabled",
                ),
                Input(
                    self.component_unique_id(self.Ids.Y_MIN_AUTO_GRAPH).to_string(),
                    "value",
                ),
                Input(
                    self.component_unique_id(self.Ids.Y_MAX_AUTO_GRAPH).to_string(),
                    "value",
                ),
            )
            def set_y_min_max(
                min_auto: List[str], max_auto: List[str]
            ) -> Tuple[bool, bool]:
                return len(min_auto) == 1, len(max_auto) == 1

            @callback(
                Output(self.component_unique_id(self.Ids.PHASE).to_string(), "options"),
                Output(self.component_unique_id(self.Ids.PHASE).to_string(), "value"),
                Input(
                    self.component_unique_id(self.Ids.GRAPH_SOURCE).to_string(), "value"
                ),
                Input(self.component_unique_id(self.Ids.ENSEMBLE).to_string(), "value"),
                State(self.component_unique_id(self.Ids.PHASE).to_string(), "value"),
            )
            def set_phases(
                source: GraphSource,
                ensemble: str,
                current_value: str,
            ) -> Tuple[List[Dict[str, str]], Union[Any, str]]:
                if ensemble is not None:
                    phases = self._menu_options[ensemble][source]["phases"]
                    options = [
                        {"label": phase.title(), "value": phase} for phase in phases
                    ]
                    return options, no_update if current_value in phases else "total"
                return [{"label": "Total", "value": "total"}], "total"

            @callback(
                Output(self.component_unique_id(self.Ids.ZONE).to_string(), "options"),
                Output(self.component_unique_id(self.Ids.ZONE).to_string(), "value"),
                Input(
                    self.component_unique_id(self.Ids.GRAPH_SOURCE).to_string(), "value"
                ),
                Input(self.component_unique_id(self.Ids.ENSEMBLE).to_string(), "value"),
                State(self.component_unique_id(self.Ids.ZONE).to_string(), "value"),
            )
            def set_zones(
                source: GraphSource,
                ensemble: str,
                current_value: str,
            ) -> Tuple[List[Dict[str, str]], Union[Any, str]]:
                if ensemble is not None:
                    zones = self._menu_options[ensemble][source]["zones"]
                    if len(zones) > 0:
                        options = [
                            {"label": zone.title(), "value": zone} for zone in zones
                        ]
                        return options, no_update if current_value in zones else "all"
                return [{"label": "All", "value": "all"}], "all"

            @callback(
                Output(
                    self.component_unique_id(self.Ids.REGION).to_string(), "options"
                ),
                Output(self.component_unique_id(self.Ids.REGION).to_string(), "value"),
                Input(
                    self.component_unique_id(self.Ids.GRAPH_SOURCE).to_string(), "value"
                ),
                Input(self.component_unique_id(self.Ids.ENSEMBLE).to_string(), "value"),
                State(self.component_unique_id(self.Ids.REGION).to_string(), "value"),
            )
            def set_regions(
                source: GraphSource,
                ensemble: str,
                current_value: str,
            ) -> Tuple[List[Dict[str, str]], Union[Any, str]]:
                if ensemble is not None:
                    regions = self._menu_options[ensemble][source]["regions"]
                    if len(regions) > 0:
                        options = [
                            {"label": reg.title(), "value": reg} for reg in regions
                        ]
                        return options, no_update if current_value in regions else "all"
                return [{"label": "All", "value": "all"}], "all"

            @callback(
                Output(
                    self.component_unique_id(self.Ids.MARK_BY).to_string(), "options"
                ),
                Output(self.component_unique_id(self.Ids.MARK_BY).to_string(), "value"),
                Output(
                    self.component_unique_id(self.Ids.ZONE_COL).to_string(), "style"
                ),
                Output(
                    self.component_unique_id(self.Ids.REGION_COL).to_string(), "style"
                ),
                Output(
                    self.component_unique_id(self.Ids.PHASE_MENU).to_string(), "style"
                ),
                Output(
                    self.component_unique_id(self.Ids.CONTAINMENT_MENU).to_string(),
                    "style",
                ),
                Output(
                    self.component_unique_id(self.Ids.PLUME_GROUP_MENU).to_string(),
                    "style",
                ),
                Input(self.component_unique_id(self.Ids.COLOR_BY).to_string(), "value"),
                Input(self.component_unique_id(self.Ids.MARK_BY).to_string(), "value"),
            )
            def organize_color_and_mark_menus(
                color_choice: str,
                mark_choice: str,
            ) -> Tuple[List[Dict], str, Dict, Dict, Dict, Dict, Dict]:
                mark_options = [
                    {"label": "Phase", "value": "phase"},
                    {"label": "None", "value": "none"},
                ]
                if self._content["zones"] and color_choice == "containment":
                    mark_options.append({"label": "Zone", "value": "zone"})
                if self._content["regions"] and color_choice == "containment":
                    mark_options.append({"label": "Region", "value": "region"})
                if self._content["plume_groups"] and color_choice == "containment":
                    mark_options.append({"label": "Plume groups", "value": "plume_group"})
                if color_choice in ["zone", "region", "plume_group"]:
                    mark_options.append(
                        {"label": "Containment", "value": "containment"}
                    )
                if mark_choice is None or mark_choice == color_choice:
                    mark_choice = "phase"
                if mark_choice in ["zone", "region"] and color_choice in [
                    "zone",
                    "region",
                ]:
                    mark_choice = "phase"
                zone, region, phase, containment, plume_group = _make_styles(
                    color_choice,
                    mark_choice,
                    self._content["zones"],
                    self._content["regions"],
                    self._content["plume_groups"],
                )
                print("CCCCCCCCCCCC")
                return mark_options, mark_choice, zone, region, phase, containment, plume_group

            @callback(
                Output(self.component_unique_id(self.Ids.ZONE).to_string(), "disabled"),
                Output(
                    self.component_unique_id(self.Ids.REGION).to_string(), "disabled"
                ),
                Input(self.component_unique_id(self.Ids.ZONE).to_string(), "value"),
                Input(self.component_unique_id(self.Ids.REGION).to_string(), "value"),
            )
            def disable_zone_or_region(zone: str, region: str) -> Tuple[bool, bool]:
                return region != "all", zone != "all"


class OpenDialogButton(html.Button):
    def __init__(self) -> None:
        super().__init__(
            LayoutLabels.COMMON_SELECTIONS,
            id=ViewSettings.Ids.OPTIONS_DIALOG_BUTTON,
            style=LayoutStyle.OPTIONS_BUTTON,
            n_clicks=0,
        )


class DialogLayout(wcc.Dialog):
    """Layout for the options dialog"""

    def __init__(
        self,
        well_names_dict: Dict[str, List[str]],
        ensembles: List[str],
    ) -> None:
        checklist_options = []
        checklist_values = []
        checklist_options.append(LayoutLabels.SHOW_FAULTPOLYGONS)
        checklist_values.append(LayoutLabels.SHOW_FAULTPOLYGONS)
        checklist_options.append(LayoutLabels.SHOW_CONTAINMENT_POLYGON)
        checklist_values.append(LayoutLabels.SHOW_CONTAINMENT_POLYGON)
        checklist_options.append(LayoutLabels.SHOW_HAZARDOUS_POLYGON)
        checklist_values.append(LayoutLabels.SHOW_HAZARDOUS_POLYGON)
        checklist_options.append(LayoutLabels.SHOW_WELLS)
        checklist_values.append(LayoutLabels.SHOW_WELLS)

        super().__init__(
            title=LayoutLabels.COMMON_SELECTIONS,
            id=ViewSettings.Ids.OPTIONS_DIALOG,
            draggable=True,
            open=False,
            children=[
                wcc.Checklist(
                    id=ViewSettings.Ids.OPTIONS_DIALOG_OPTIONS,
                    options=[{"label": opt, "value": opt} for opt in checklist_options],
                    value=checklist_values,
                ),
                wcc.FlexBox(
                    children=[
                        html.Div(
                            id=ViewSettings.Ids.WELL_FILTER_HEADER,
                            style={
                                "flex": 3,
                                "minWidth": "20px",
                                "display": (
                                    "block" if well_names_dict[ensembles[0]] else "none"
                                ),
                            },
                            children=WellFilter(well_names_dict, ensembles),
                        ),
                    ],
                    style={"width": "20vw"},
                ),
            ],
        )


class WellFilter(html.Div):
    def __init__(
        self, well_names_dict: Dict[str, List[str]], ensembles: List[str]
    ) -> None:
        super().__init__(
            children=wcc.SelectWithLabel(
                style={"display": "block" if well_names_dict[ensembles[0]] else "none"},
                label=LayoutLabels.WELL_FILTER,
                id=ViewSettings.Ids.OPTIONS_DIALOG_WELL_FILTER,
                options=[
                    {"label": i, "value": i} for i in well_names_dict[ensembles[0]]
                ],
                value=well_names_dict[ensembles[0]],
                size=min(20, len(well_names_dict[ensembles[0]])),
            ),
        )


class FilterSelectorLayout(wcc.Selectors):
    def __init__(self, formation_id: str):
        super().__init__(
            label="Filter Settings",
            children=[
                "Formation",
                wcc.Dropdown(
                    id=formation_id,
                    clearable=False,
                ),
            ],
        )


class OpenVisualizationThresholdsButton(html.Button):
    def __init__(self) -> None:
        super().__init__(
            LayoutLabels.VISUALIZATION_THRESHOLDS,
            id=ViewSettings.Ids.VISUALIZATION_THRESHOLD_BUTTON,
            style=LayoutStyle.THRESHOLDS_BUTTON,
            n_clicks=0,
        )


class VisualizationThresholdsLayout(wcc.Dialog):
    """Layout for the visualization thresholds dialog"""

    def __init__(
        self,
        ids: List[str],
        thresholds: MapThresholds,
        visualization_update_id: str,
    ) -> None:
        standard_thresholds = thresholds.standard_thresholds

        fields = [
            html.Div(
                "Here you can select a filter for the visualization of the map, "
                "hiding values smaller than the selected minimum cutoff. "
                "After changing the threshold value, press 'Update' to have the map reappear. "
                "A value of -1 can be used to visualize zeros."
            ),
            html.Div("", style={"height": "30px"}),
            html.Div(
                [
                    html.Div("Property:", style={"width": "42%"}),
                    html.Div("Standard cutoff:", style={"width": "32%"}),
                    html.Div("Minimum cutoff:", style={"width": "25%"}),
                ],
                style={"display": "flex", "flex-direction": "row"},
            ),
        ]
        fields += [
            html.Div(
                [
                    html.Div(id, style={"width": "42%"}),
                    html.Div(standard_thresholds[id], style={"width": "32%"}),
                    dcc.Input(
                        id=id,
                        type="number",
                        value=standard_thresholds[id],
                        step="0.0005",
                        style={"width": "25%"},
                    ),
                ],
                style={"display": "flex", "flex-direction": "row"},
            )
            for id in ids
        ]
        fields.append(html.Div(style={"height": "20px"}))
        fields.append(
            html.Div(
                [
                    html.Div(style={"width": "80%"}),
                    html.Button(
                        "Update",
                        id=visualization_update_id,
                        style=LayoutStyle.VISUALIZATION_BUTTON,
                        n_clicks=0,
                    ),
                ],
                style={"display": "flex", "flex-direction": "row"},
            )
        )
        super().__init__(
            title=LayoutLabels.VISUALIZATION_THRESHOLDS,
            id=ViewSettings.Ids.VISUALIZATION_THRESHOLD_DIALOG,
            draggable=True,
            open=False,
            children=html.Div(
                fields, style={"flex-direction": "column", "width": "500px"}
            ),
        )


class MapSelectorLayout(wcc.Selectors):
    _CM_RANGE = {
        "display": "flex",
        "flexDirection": "row",
    }

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        color_scale_names: List[str],
        property_id: str,
        statistic_id: str,
        colormap_id: str,
        cm_min_id: str,
        cm_max_id: str,
        cm_min_auto_id: str,
        cm_max_auto_id: str,
        mass_unit_id: str,
        mass_unit_update_id: str,
        map_attribute_names: FilteredMapAttribute,
    ):
        default_colormap = (
            "turbo (Seq)"
            if "turbo (Seq)" in color_scale_names
            else color_scale_names[0]
        )
        super().__init__(
            label="Map Settings",
            open_details=True,
            children=[
                html.Div(
                    [
                        "Property",
                        wcc.Dropdown(
                            id=property_id,
                            options=_compile_property_options(map_attribute_names),
                            value=next(iter(map_attribute_names.filtered_values)).value,
                            clearable=False,
                        ),
                        "Statistic",
                        wcc.Dropdown(
                            id=statistic_id,
                            options=[s.value for s in SurfaceStatistic],
                            value=SurfaceStatistic.MEAN,
                            clearable=False,
                        ),
                        html.Div(
                            style={
                                "height": "1px",
                                "backgroundColor": "lightgray",
                                "gridColumnStart": "span 2",
                            }
                        ),
                        "Color Scale",
                        dcc.Dropdown(
                            id=colormap_id,
                            options=color_scale_names,
                            value=default_colormap,
                            clearable=False,
                        ),
                        "Minimum",
                        html.Div(
                            [
                                dcc.Input(id=cm_min_id, type="number"),
                                dcc.Checklist(
                                    ["Auto"],
                                    ["Auto"],
                                    id=cm_min_auto_id,
                                ),
                            ],
                            style=self._CM_RANGE,
                        ),
                        "Maximum",
                        html.Div(
                            [
                                dcc.Input(id=cm_max_id, type="number"),
                                dcc.Checklist(
                                    ["Auto"],
                                    ["Auto"],
                                    id=cm_max_auto_id,
                                ),
                            ],
                            style=self._CM_RANGE,
                        ),
                        "Mass unit (for mass maps)",
                        html.Div(
                            [
                                html.Div(
                                    wcc.Dropdown(
                                        id=mass_unit_id,
                                        options=["kg", "tons", "M tons"],
                                        value="tons",
                                        clearable=False,
                                    ),
                                    style={"width": "50%"},
                                ),
                                html.Button(
                                    "Update unit",
                                    id=mass_unit_update_id,
                                    style=LayoutStyle.VISUALIZATION_BUTTON,
                                    n_clicks=0,
                                ),
                            ],
                            style={"display": "flex"},
                        ),
                        OpenVisualizationThresholdsButton(),
                    ],
                )
            ],
        )


class GraphSelectorsLayout(wcc.Selectors):
    _CM_RANGE = {
        "display": "flex",
        "flexDirection": "row",
    }

    def __init__(
        self,
        graph_source_id: str,
        co2_scale_id: str,
        y_min_ids: List[str],
        y_max_ids: List[str],
        containment_ids: List[str],
        content: Dict[str, bool],
    ):
        print("\n\ncontent:")
        print(content)
        disp_zone = "flex" if content["zones"] else "none"
        disp_region = "flex" if content["regions"] else "none"
        disp_plume_group = "flex" if content["plume_groups"] else "none"
        color_options = [{"label": "Containment (standard)", "value": "containment"}]
        mark_options = [{"label": "Phase", "value": "phase"}]
        if content["zones"]:
            color_options.append({"label": "Zone", "value": "zone"})
            mark_options.append({"label": "Zone", "value": "zone"})
        if content["regions"]:
            color_options.append({"label": "Region", "value": "region"})
            mark_options.append({"label": "Region", "value": "region"})
        if content["plume_groups"]:
            color_options.append({"label": "Plume group", "value": "plume_group"})
            mark_options.append({"label": "Plume group", "value": "plume_group"})
        source_options = []
        if content["mass"]:
            source_options.append(GraphSource.CONTAINMENT_MASS)
        if content["volume"]:
            source_options.append(GraphSource.CONTAINMENT_ACTUAL_VOLUME)
        if content["unsmry"]:
            source_options.append(GraphSource.UNSMRY)
        unit_options, init_unit = (
            (list(Co2VolumeScale), Co2VolumeScale.BILLION_CUBIC_METERS)
            if source_options[0] == GraphSource.CONTAINMENT_ACTUAL_VOLUME
            else (list(Co2MassScale), Co2MassScale.MTONS)
        )
        super().__init__(
            label="Graph Settings",
            open_details=not content["maps"],
            children=[
                "Source",
                wcc.Dropdown(
                    id=graph_source_id,
                    options=source_options,
                    value=source_options[0],
                    clearable=False,
                ),
                "Unit",
                wcc.Dropdown(
                    id=co2_scale_id,
                    options=unit_options,
                    value=init_unit,
                    clearable=False,
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                "Color by",
                                wcc.Dropdown(
                                    options=color_options,
                                    value="containment",
                                    id=containment_ids[0],
                                    clearable=False,
                                ),
                            ],
                            style={
                                "width": "50%",
                                "flex-direction": "column",
                            },
                        ),
                        html.Div(
                            [
                                "Mark by",
                                wcc.Dropdown(
                                    options=mark_options,
                                    value="phase",
                                    id=containment_ids[1],
                                    clearable=False,
                                ),
                            ],
                            style={
                                "width": "50%",
                                "flex-direction": "column",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flex-direction": "row",
                        "margin-top": "10px",
                        "margin-bottom": "1px",
                    },
                ),
                html.Div(
                    [
                        "Sort by",
                        dcc.RadioItems(
                            options=["color", "marking"],
                            value="color",
                            id=containment_ids[2],
                            inline=True,
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flex-direction": "row",
                        "margin-top": "5px",
                        "margin-bottom": "1px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                "Zone",
                                wcc.Dropdown(
                                    options=[{"label": "All", "value": "all"}],
                                    value="all",
                                    id=containment_ids[3],
                                    clearable=False,
                                ),
                            ],
                            id=containment_ids[4],
                            style={
                                # "width": "50%" if content["regions"] else "100%",
                                "width": "33%" if (content["regions"] + content["plume_groups"]) else "100%",  # NBNB-AS
                                "display": disp_zone,
                                "flex-direction": "column",
                            },
                        ),
                        html.Div(
                            [
                                "Region",
                                wcc.Dropdown(
                                    options=[{"label": "All", "value": "all"}],
                                    value="all",
                                    id=containment_ids[5],
                                    clearable=False,
                                ),
                            ],
                            id=containment_ids[6],
                            style={
                                # "width": "50%" if content["zones"] else "100%",
                                "width": "33%" if (content["zones"] + content["plume_groups"]) else "100%",  # NBNB-AS
                                "display": disp_region,
                                "flex-direction": "column",
                            },
                        ),
                        html.Div(
                            [
                                "Phase",
                                wcc.Dropdown(
                                    options=[{"label": "Total", "value": "total"}],
                                    value="total",
                                    clearable=False,
                                    id=containment_ids[8],
                                ),
                            ],
                            id=containment_ids[9],
                            style={"display": "none"},
                        ),
                        html.Div(
                            [
                                "Containment",
                                wcc.Dropdown(
                                    options=[
                                        {"label": "Total", "value": "total"},
                                        {"label": "Contained", "value": "contained"},
                                        {"label": "Outside", "value": "outside"},
                                        {"label": "Hazardous", "value": "hazardous"},
                                    ],
                                    value="total",
                                    clearable=False,
                                    id=containment_ids[10],
                                ),
                            ],
                            id=containment_ids[11],
                            style={"display": "none"},
                        ),
                        html.Div(
                            [
                                "Plume",
                                wcc.Dropdown(
                                    options=[{"label": "All", "value": "all"}],
                                    value="all",
                                    id=containment_ids[12],
                                    clearable=False,
                                ),
                            ],
                            id=containment_ids[13],
                            style={
                                "width": "33%" if (content["zones"]+content["regions"]) else "100%",  # NBNB-AS
                                "display": disp_plume_group,
                                "flex-direction": "column",
                            },
                        ),
                    ],
                    id=containment_ids[7],
                    style={"display": "flex"},
                ),
                html.Div(
                    "Fix y-limits in third plot:",
                    style={"margin-top": "10px"},
                ),
                "Minimum",
                html.Div(
                    [
                        dcc.Input(id=y_min_ids[0], type="number"),
                        dcc.Checklist(
                            ["Auto"],
                            ["Auto"],
                            id=y_min_ids[1],
                        ),
                    ],
                    style=self._CM_RANGE,
                ),
                "Maximum",
                html.Div(
                    [
                        dcc.Input(id=y_max_ids[0], type="number"),
                        dcc.Checklist(
                            ["Auto"],
                            ["Auto"],
                            id=y_max_ids[1],
                        ),
                    ],
                    style=self._CM_RANGE,
                ),
            ],
        )


class ExperimentalFeaturesLayout(wcc.Selectors):
    def __init__(self, plume_threshold_id: str, plume_smoothing_id: str):
        super().__init__(
            label="Experimental",
            open_details=False,
            children=[
                html.Div(
                    children=[
                        html.Div("Plume Threshold"),
                        dcc.Input(
                            id=plume_threshold_id,
                            type="number",
                            min=0,
                            value=0.000001,
                            placeholder="Lower property threshold",
                            style={
                                "textAlign": "right",
                            },
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div("Plume Smoothing"),
                        dcc.Input(
                            id=plume_smoothing_id,
                            type="number",
                            min=0,
                            value=0,
                            step=1,
                            placeholder="Smoothing [#pixels]",
                            style={
                                "textAlign": "right",
                            },
                        ),
                    ],
                ),
            ],
        )


class EnsembleSelectorLayout(wcc.Selectors):
    def __init__(self, ensemble_id: str, realization_id: str, ensembles: List[str]):
        super().__init__(
            label="Ensemble",
            open_details=True,
            children=[
                "Ensemble",
                wcc.Dropdown(
                    id=ensemble_id,
                    options=[{"value": en, "label": en} for en in ensembles],
                    value=ensembles[0],
                    clearable=False,
                ),
                "Realization",
                wcc.SelectWithLabel(
                    id=realization_id,
                    value=[],
                    multi=True,
                ),
            ],
        )


def _create_left_side_menu(
    map_group: str, map_attribute_names: FilteredMapAttribute
) -> List:
    title = {
        "label": html.Span([f"{map_group}:"], style={"text-decoration": "underline"}),
        "value": "",
        "disabled": True,
    }
    map_attribute_list = [
        {"label": MapAttribute[key.name].value, "value": MapAttribute[key.name].value}
        for key in map_attribute_names.filtered_values.keys()
        if MapGroup[key.name].value == map_group
    ]
    return [title] + map_attribute_list


def _compile_property_options(
    map_attribute_names: FilteredMapAttribute,
) -> List[Dict[str, Any]]:
    requested_map_groups = [
        MapGroup[key.name].value for key in map_attribute_names.filtered_values.keys()
    ]
    unique_requested_map_groups = list(set(requested_map_groups))
    return [
        element
        for group in unique_requested_map_groups
        for element in _create_left_side_menu(group, map_attribute_names)
    ]


class FeedbackLayout(wcc.Dialog):
    """Layout for the feedback button"""

    def __init__(
        self,
    ) -> None:
        super().__init__(
            title=LayoutLabels.FEEDBACK,
            id=ViewSettings.Ids.FEEDBACK,
            draggable=True,
            open=False,
            children=[
                dcc.Markdown(
                    """If you have any feedback regarding the CO2-Leakage application,
                    don't hesitate to"""
                ),
                dcc.Link(
                    ["send an email!"],
                    href=f"mailto:{get_emails()}&subject=Feedback regarding the "
                    f"CO2-Leakage application",
                    target="_blank",
                    style={"float": "left"},
                ),
            ],
        )


class FeedbackButton(html.Button):
    def __init__(self) -> None:
        style = LayoutStyle.FEEDBACK_BUTTON
        super().__init__(
            LayoutLabels.FEEDBACK,
            id=ViewSettings.Ids.FEEDBACK_BUTTON,
            style=style,
            n_clicks=0,
        )


def decrypt_email(encrypted_email: str, key: int) -> str:
    decrypted_email = []
    for char in encrypted_email:
        decrypted_email.append(chr(ord(char) ^ key))
    return "".join(decrypted_email)


def get_emails() -> str:
    emails = [
        decrypt_email(m, i + 1)
        for i, m in enumerate(
            [
                "GLLNAdpthons/bnl",
                "`ijBgswklmp,amo",
                "pfhCmq-ml",
                "bjarnajDjv*jk",
                "vlfdfmdEkw+kj",
            ]
        )
    ]
    return ";".join(emails[:2]) + "?cc=" + ";".join(emails[2:])


def _make_styles(
    color_choice: str,
    mark_choice: str,
    has_zones: bool,
    has_regions: bool,
    has_plume_groups: bool,
) -> List[Dict[str, str]]:
    print("\n_make_styles()")
    zone = {"display": "none", "flex-direction": "column", "width": "100%"}
    region = {"display": "none", "flex-direction": "column", "width": "100%"}
    phase = {"display": "none", "flex-direction": "column", "width": "100%"}
    containment = {"display": "none", "flex-direction": "column", "width": "100%"}
    plume_group = {"display": "none", "flex-direction": "column", "width": "100%"}
    if color_choice == "containment":
        if mark_choice == "phase":
            zone["display"] = "flex" if has_zones else "none"
            region["display"] = "flex" if has_regions else "none"
            plume_group["display"] = "flex" if has_plume_groups else "none"
            n_categories = has_regions + has_zones + has_plume_groups
            if n_categories == 3:
                zone["width"] = region["width"] = plume_group["width"] = "33%"
            elif n_categories == 2:
                zone["width"] = region["width"] = plume_group["width"] = "50%"
            else:
                zone["width"] = region["width"] = plume_group["width"] = "100%"
        elif mark_choice == "none":
            zone["display"] = "flex" if has_zones else "none"
            region["display"] = "flex" if has_regions else "none"
            plume_group["display"] = "flex" if has_plume_groups else "none"
            phase["display"] = "flex"
            n_categories = 1 + has_regions + has_zones + has_plume_groups
            if n_categories == 4:
                phase["width"] = zone["width"] = region["width"] = plume_group["width"] = "25%"
            elif n_categories == 3:
                phase["width"] = zone["width"] = region["width"] = plume_group["width"] = "33%"
            elif n_categories == 2:
                phase["width"] = zone["width"] = region["width"] = plume_group["width"] = "50%"
            else:
                phase["width"] = zone["width"] = region["width"] = plume_group["width"] = "100%"
            # zone["width"] = "33%" if has_regions else "50%"
            # region["width"] = "33%" if has_zones else "50%"
            # phase["width"] = (
            #     "33%"
            #     if has_zones and has_regions
            #     else "100%"
            #     if not has_regions and not has_zones
            #     else "50%"
            # )
        else:  # mark_choice == "zone" / "region"
            phase["display"] = "flex"
    else:  # color_choice == "zone" / "region"
        if mark_choice == "phase":
            containment["display"] = "flex"
        elif mark_choice == "none":
            containment["width"] = "50%"
            containment["display"] = "flex"
            phase["width"] = "50%"
            phase["display"] = "flex"
        else:  # mark == "containment"
            phase["display"] = "flex"
    return [zone, region, phase, containment, plume_group]
