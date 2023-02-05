from typing import Dict, List

from dash import html
from dash.development.base_component import Component
import webviz_core_components as wcc

from webviz_config.utils import StrEnum
from webviz_config.webviz_plugin_subclasses import SettingsGroupABC


class ViewSettings(SettingsGroupABC):
    class Ids(StrEnum):
        ENSEMBLE = "ensemble"
        # REALIZATION = "realization"

    def __init__(
        self,
        ensemble_paths: Dict[str, str]
    ):
        print("Running ViewSettings.__init__()")
        super().__init__("Settings")
        self._ensemble_paths = ensemble_paths
        print("Done ViewSettings.__init__()")

    def layout(self) -> List[Component]:
        return [
            EnsembleSelectorLayout(
                self.register_component_unique_id(self.Ids.ENSEMBLE),
                list(self._ensemble_paths.keys()))
        ]

    def layout_old(self) -> html.Div:
        return html.Div([
            html.H1('Settings title?'),
            'And this is just some ordinary text'
        ])

class EnsembleSelectorLayout(wcc.Selectors):
    def __init__(self, ensemble_id: str, ensembles: List[str]):
        super().__init__(
            label="Ensemble",
            open_details=True,
            children=[
                "Ensemble",
                wcc.Dropdown(
                    id=ensemble_id,
                    options=[dict(value=en, label=en) for en in ensembles],
                    value=ensembles[0],
                    clearable=False,
                ),
            ],
        )
