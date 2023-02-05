import warnings
from typing import Dict, List, Tuple

from dash import Dash, html, callback, Input, Output, no_update
import plotly.graph_objects as go

from webviz_config import WebvizPluginABC, WebvizSettings

from . import _error
from webviz_subsurface.plugins._plume_stability.views.mainview.mainview import (
    MainView,
    MapViewElement
)
from webviz_subsurface.plugins._plume_stability.views.mainview.settings import ViewSettings
from webviz_subsurface.plugins._plume_stability._utilities.initialization import (
    init_table_provider
)
from webviz_subsurface.plugins._plume_stability._utilities.plume_extent import generate_plume_extent_figure
from webviz_config.utils import StrEnum, callback_typecheck



class PlumeStability(WebvizPluginABC):
    """
    Plugin for analyzing plume stability
    """

    class Ids(StrEnum):
        MAIN_VIEW = "main-view"
        MAIN_SETTINGS = "main-settings"

    def __init__(
        self,
        app: Dash,
        webviz_settings: WebvizSettings,
        ensembles: List[str],
        plume_extent_relpath: str = "share/results/tables/plume_extent.csv"
    ):
        print("Running PlumeStability.__init__()")
        super().__init__()
        print("Done WebvizPluginABC.__init__()")

        self._error_message = ""

        try:
            if False:
                raise Exception("Something wrong")
            elif False:
                raise TypeError("Wrong type")

            self._ensemble_paths = {
                ensemble_name: webviz_settings.shared_settings["scratch_ensembles"][
                    ensemble_name
                ]
                for ensemble_name in ensembles
            }
            print("self._ensemble_paths:")
            print(self._ensemble_paths)

            print("plume_extent_relpath:")
            print(plume_extent_relpath)
            self._plume_extent_table_providers = init_table_provider(
                self._ensemble_paths,
                plume_extent_relpath,
            )
            print(self._plume_extent_table_providers)

        except Exception as err:
            self._error_message = f"Plugin initialization failed: {err}"
            raise

        print("add_shared_settings_group()")
        self.add_shared_settings_group(
            ViewSettings(
                self._ensemble_paths
            ),
            self.Ids.MAIN_SETTINGS,
        )

        print("add_view()   [MainView]")
        self.add_view(MainView(), self.Ids.MAIN_VIEW)

        print("Done PlumeStability.__init__()")

    @property
    def layout(self) -> html.Div:
        print("Running PlumeStability.layout()")
        return _error.error(self._error_message)

    def _view_component(self, component_id: str) -> str:
        return (
            self.view(self.Ids.MAIN_VIEW)
            .view_element(MainView.Ids.MAIN_ELEMENT)
            .component_unique_id(component_id)
            .to_string()
        )

    def _settings_component(self, component_id: str) -> str:
        return (
            self.shared_settings_group(self.Ids.MAIN_SETTINGS)
            .component_unique_id(component_id)
            .to_string()
        )

    def _set_callbacks(self) -> None:
        print("_set_callbacks()")
        @callback(
            Output(self._view_component(MapViewElement.Ids.EXTENT_PLOT), "figure"),
            Output(self._view_component(MapViewElement.Ids.EXTENT_PLOT), "style"),
            Input(self._settings_component(ViewSettings.Ids.ENSEMBLE), "value"),
        )
        @callback_typecheck
        def update_graphs(ensemble: str) -> Tuple[go.Figure, Dict]:
            print("@callback: update_graphs()")
            styles = [{"display": "none"}] * 1
            figs = [no_update] * 1

            if ensemble in self._plume_extent_table_providers:
                print("OK!")

                fig_args = (
                    self._plume_extent_table_providers[ensemble],
                    self._plume_extent_table_providers[ensemble].realizations()
                )
                try:
                    figs[0] = generate_plume_extent_figure(*fig_args)
                    styles = [{}] * 1
                except KeyError as exc:
                    warnings.warn(f"Could not generate plume extent figure: {exc}")
                    raise exc
            return *figs, *styles  # type: ignore

    @property
    def layoutOld(self) -> html.Div:
        print("Running PlumeStability.layout()")
        return html.Div([
                         html.H1('This is a static title'),
                         'And this is just some ordinary text'
                        ])
