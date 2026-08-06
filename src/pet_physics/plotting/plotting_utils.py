"""This module contains functions for plotting results of the MuJoCo simulation."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pet_physics.plotting.axis_info import AxisInfo


def create_interactive_line_chart(
    x_axis: AxisInfo,
    y1_axis: AxisInfo,
    y2_axis: AxisInfo | None = None,
    title: str | None = None,
    show_points: bool = True,
) -> go.Figure:
    """Creates an interactive line chart using plotly.

    If `y2_axis` is provided, its data points are displayed on a secondary
    y-axis in the same plot.

    Args:
        x_axis: The name, values, and label of the x-axis.
        y1_axis: The name, values, and label of the primary y-axis.
        y2_axis: The name, values, and label of the secondary y-axis. If None, no secondary axis is shown.
        title: The title of the plot. Auto-generated if None.
        show_points: Whether to display markers for data points.

    Returns:
        The interactive line chart figure.
    """
    COLOR_Y1 = "royalblue"
    COLOR_Y2 = "red"

    # check whether we need secondary y axis
    secondary_y = y2_axis is not None

    fig = make_subplots(specs=[[{"secondary_y": secondary_y}]])

    # Add the line trace
    fig.add_trace(
        go.Scatter(
            x=x_axis.values,
            y=y1_axis.values,
            mode="lines+markers" if show_points else "lines",
            name=y1_axis.name,
            line=dict(color=COLOR_Y1, width=2),
            marker=dict(size=8) if show_points else None,
            hovertemplate="<b>%{x}</b>: %{y:.3f}<extra></extra>",
        ),
        secondary_y=False,
    )

    # add second line trace
    if secondary_y:
        fig.add_trace(
            go.Scatter(
                x=x_axis.values,
                y=y2_axis.values,
                mode="lines+markers" if show_points else "lines",
                name=y2_axis.name,
                line=dict(color=COLOR_Y2, width=2),
                marker=dict(size=8) if show_points else None,
                hovertemplate="<b>%{x}</b>: %{y:.3f}<extra></extra>",
            ),
            secondary_y=True,
        )

    if title is None:
        optional_title_part = f"/{y2_axis.name}" if secondary_y else ""
        title = f"{y1_axis.name}{optional_title_part} over {x_axis.name}"

    # Update layout with title and axis labels
    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center", "font": dict(size=22)},
        xaxis_title=x_axis.label,
        hovermode="closest",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # set labels for y axes
    fig.update_yaxes(title_text=y1_axis.label, title_font=dict(color=COLOR_Y1), secondary_y=False)

    if secondary_y:
        fig.update_yaxes(title_text=y2_axis.label, title_font=dict(color=COLOR_Y2), secondary_y=True)

    # Add interactive features
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="linear"))  # Add range slider

    return fig
