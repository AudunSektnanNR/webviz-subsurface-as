from typing import Any, Dict, List

import plotly.graph_objects as go
import webviz_core_components as wcc
from dash import html
from dash.development.base_component import Component
from webviz_config.utils import StrEnum
from webviz_config.webviz_plugin_subclasses import ViewABC, ViewElementABC
from webviz_subsurface_components import DeckGLMap


class MainView(ViewABC):
    class Ids(StrEnum):
        MAIN_ELEMENT = "main-element"

    def __init__(self):
        super().__init__("Main View")
        self._view_element = MapViewElement()
        self.add_view_element(self._view_element, self.Ids.MAIN_ELEMENT)


class MapViewElement(ViewElementABC):
    class Ids(StrEnum):
        EXTENT_PLOT = "extent-plot"

    def __init__(self) -> None:
        print("Running MapViewElement.__init__()")
        super().__init__()

    def inner_layout(self) -> Component:
        print("Running MapViewElement.inner_layout()")
        return html.Div(
            [
                wcc.Frame(color="#F0FFF0",
                          highlight=False,
                          children=self._top_graphs_layout(),
                          style={
                              # "padding": "1vh",
                              # "width": "25vh",
                              "height": "40vh",
                              # "position": "relative",
                              # "backgroundColor": "#F0FFF0",
                              "display": "flex",
                              # "align-items": "stretch"
                              "flexDirection": "row",
                              "justifyContent": "space-evenly",
                          }),
                wcc.Frame(color="#B0C4DE",
                          highlight=False,
                          children=self._bottom_graphs_layout(
                              self.register_component_unique_id(self.Ids.EXTENT_PLOT)
                          ),
                          style={
                              # "padding": "1vh",
                              # "width": "25vh",
                              "height": "40vh",
                              # "position": "relative",
                              # "backgroundColor": "#B0C4DE",
                              "display": "flex",
                              # "align-items": "stretch"
                              "flexDirection": "row",
                              "justifyContent": "space-evenly",
                          })
            ],
            style={
                "flex": 3,
                "display": "flex",
                "flexDirection": "column",
                'backgroundColor': '#BBBBBB'
            },
        )

    def _top_graphs_layout(self):
        return [
            html.Div(["Frame 1"],
                     style={
                         "backgroundColor": "#DAA520",
                     }),
            html.Div(["Frame 2"],
                     style={
                         "backgroundColor": "#D8BFD8",
                     })
        ]

    def _bottom_graphs_layout(self, extent_plot_id: str):
        import numpy as np
        x = np.arange(10)
        fig = go.Figure(data=go.Scatter(x=x, y=x ** 2))
        print("extent_plot_id = " + str(extent_plot_id))
        return [
            wcc.Graph(
                # id=extent_plot_id+"2",
                id=extent_plot_id,
                # figure=go.Figure(),
                figure=fig,
                config={
                    "displayModeBar": False,
                },
            ),
            # html.Div(["Frame 3"],
            #          style={
            #              "backgroundColor": "#9ACD32",
            #          }),
            html.Div(["Frame 4"],
                     style={
                         "backgroundColor": "#FFF8DC",
                     }),
        ]

    def inner_layout2(self) -> Component:
        print("Running MapViewElement.inner_layout()")
        return html.Div(
            [
                html.Div(["Frame 1"],
                         style={
                             "padding": "1vh",
                             "width": "25vh",
                             "height": "25vh",
                             "position": "relative",
                             "backgroundColor": "#FF7F50",
                             "display": "flex",
                             "align-items": "stretch"
                         }),
                html.Div(["Frame 2"],
                         style={
                             "padding": "1vh",
                             "width": "25vh",
                             "height": "25vh",
                             "position": "relative",
                             "backgroundColor": "#98FB98",
                             "display": "flex"
                         }),
                html.Div(["Frame 3"],
                         style={
                             "padding": "1vh",
                             "width": "25vh",
                             "height": "25vh",
                             "position": "relative",
                             "backgroundColor": "#AFEEEE",
                             "display": "flex"
                         }),
                wcc.Frame(color="white",
                          children=[html.Div(["Frame 4"], style={"backgroundColor": "#aaff77"})],
                          style={
                              "padding": "1vh",
                              "width": "25vh",
                              "height": "25vh",
                              "position": "relative",
                              "backgroundColor": "#FFF8DC",
                              "display": "flex"
                          })
            ],
            style={
                "flex": 3,
                "display": "flex",
                "flexDirection": "column",
                'backgroundColor': '#BBBBBB'  # #FF7F50  #98FB98  #AFEEEE  #FFF8DC
            },
        )
