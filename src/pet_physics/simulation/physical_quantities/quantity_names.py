"""Defines the names for different quantity histories."""

from enum import StrEnum


class QuantityName(StrEnum):
    """Provides the names for different quantity histories.

    Attributes:
        ACCELERATION: The name for the acceleration history.
        FORCE: The name for the force history.
        N_CONTACTS: The name for the number of contacts history.
        PENETRATION: The name for the penetration history.
        POSE: The name for the pose history.
    """

    ACCELERATION = "acceleration"
    FORCE = "force"
    N_CONTACTS = "n_contacts"
    PENETRATION = "penetration"
    POSE = "pose"
