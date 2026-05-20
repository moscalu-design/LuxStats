"""Reusable Plotly chart builders."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PORTAL_COLORS = ["#2f6f73", "#c9822b", "#6b8f71", "#6f5e9c", "#b85042", "#427aa1"]


def _layout(fig: go.Figure, title: str | None = None) -> go.Figure:
    fig.update_layout(
        title=title,
        colorway=PORTAL_COLORS,
        hovermode="x unified",
        legend_title_text="",
        margin=dict(l=10, r=10, t=52 if title else 24, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#edf1f5", zerolinecolor="#d8dee6")
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str | None = None) -> go.Figure:
    plot_df = df.sort_values(x) if x in df.columns else df
    fig = px.line(plot_df, x=x, y=y, color=color, markers=True)
    return _layout(fig, title)


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str | None = None) -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, barmode="group")
    return _layout(fig, title)


def ranked_bar_chart(df: pd.DataFrame, label_col: str, value_col: str, top_n: int = 20, title: str | None = None) -> go.Figure:
    plot_df = df.sort_values(value_col, ascending=True).tail(top_n)
    fig = px.bar(plot_df, x=value_col, y=label_col, orientation="h")
    return _layout(fig, title)


def decile_chart(df: pd.DataFrame, decile_col: str, value_col: str, title: str | None = None) -> go.Figure:
    plot_df = df.sort_values(decile_col)
    fig = px.bar(plot_df, x=decile_col, y=value_col)
    return _layout(fig, title)


def map_placeholder(title: str = "Map view coming later") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text="Commune map needs boundary data before it can be shown responsibly.",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _layout(fig, title)
