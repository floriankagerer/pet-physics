"""Data class describing a body that dropped during the simulation."""

from dataclasses import dataclass


@dataclass
class DroppedBody:
    """Information about a body that dropped during the simulation.

    Attributes:
        name: The name of the body that dropped.
        drop_timestamp: When the drop happened, e.g., a pose history index or a timestamp in seconds.
    """

    name: str
    drop_timestamp: int | float
