"""Represents the information about an axis of a plot."""

from dataclasses import dataclass


@dataclass
class AxisInfo:
    """Contains the information about an axis of a plot.

    Attributes:
        name: The name of the data points.
        values: The value of each data point.
        label: The label of the axis.
    """

    name: str
    values: list[float | int]
    label: str
