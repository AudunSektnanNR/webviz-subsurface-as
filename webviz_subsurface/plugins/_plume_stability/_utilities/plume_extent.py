import itertools
from enum import Enum
from typing import List

import numpy as np
import pandas
import plotly.express as px
import plotly.graph_objects as go

from webviz_subsurface._providers import EnsembleTableProvider


class _Columns(Enum):
    REALIZATION = "realization"
    VOLUME = "volume"
    CONTAINMENT = "containment"
    VOLUME_OUTSIDE = "volume_outside"


def _read_dataframe(
    table_provider: EnsembleTableProvider, realization: int
) -> pandas.DataFrame:
    return table_provider.get_column_data(
        ["DATE", "MAX_DISTANCE_SGAS", "MAX_DISTANCE_AMFG"], [realization]
    )


def _read_plume_extent(
    table_provider: EnsembleTableProvider, realizations: List[int]
) -> pandas.DataFrame:
    return pandas.concat(
        [
            _read_dataframe(table_provider, real).assign(realization=real)
            for real in realizations
        ]
    )


def generate_plume_extent_figure(
    table_provider: EnsembleTableProvider,
    realizations: List[int],
) -> go.Figure:
    print("generate_plume_extent_figure")
    df = _read_plume_extent(table_provider, realizations)
    print(df)
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly
    # # Generate dummy scatters for legend entries
    sgas_args = dict(line_dash="dot", legendgroup="SGAS", name="SGAS")
    amfg_args = dict(legendgroup="AMFG", name="AMFG")
    # dummy_args = dict(mode="lines", marker_color="black", hoverinfo="none")
    # fig.add_scatter(y=[0.0], **dummy_args, **outside_args)
    # fig.add_scatter(y=[0.0], **dummy_args, **total_args)
    for rlz, color in zip(realizations, itertools.cycle(colors)):
        print("color = " + str(color))
        sub_df = df[df["realization"] == rlz]
        common_args = dict(
            x=sub_df["DATE"],
            hovertemplate="%{x}: %{y}<br>Realization: %{meta[0]}",
            meta=[rlz],
            marker_color=color,
            showlegend=False,
        )
        fig.add_scatter(y=sub_df["MAX_DISTANCE_SGAS"], **sgas_args, **common_args)
        fig.add_scatter(y=sub_df["MAX_DISTANCE_AMFG"], **amfg_args, **common_args)
    # fig.layout.legend.orientation = "h"
    # fig.layout.legend.title.text = ""
    # fig.layout.legend.y = -0.3
    fig.layout.title = "Plume extent"
    # fig.layout.xaxis.title = "Time"
    # fig.layout.yaxis.title = scale.value
    # fig.layout.yaxis.exponentformat = "none"
    # fig.layout.yaxis.range = (0, 1.05 * df["total"].max())
    # _adjust_figure(fig)
    print("END generate_plume_extent_figure()")
    return fig
