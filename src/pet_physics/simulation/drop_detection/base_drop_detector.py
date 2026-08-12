"""This module contains the base class for any body drop detector."""

from abc import ABC
from functools import cached_property

from pet_physics.constants import BELOWNESS_THRESHOLD, Z_COORDINATE_TOP_SIDE_OF_CARRIER


class BaseDropDetector(ABC):
    """The base class for any body drop detector."""

    def __init__(
        self,
        distance_below_top_side_of_carrier_to_consider_as_not_touching_floor: float | None = None,
    ) -> None:
        """The constructor of this class.

        Args:
            distance_below_top_side_of_carrier_to_consider_as_not_touching_floor: This value defines
                the distance below the top side of the carrier such that a body is not considered as touching the floor.
                If `None`, a default value is used (`0.1`, meaning, 0.1 meters).
        """

        self._distance_below_top_side_of_carrier_to_consider_as_not_touching_floor = (
            distance_below_top_side_of_carrier_to_consider_as_not_touching_floor or BELOWNESS_THRESHOLD
        )
        """This value defines the distance below the top side of the carrier such that a body is not considered as
        touching the floor."""

    @cached_property
    def z_coordinate_defining_floor_contact(self) -> float:
        """The z-coordinate that defines whether a body is considered as touching the floor."""
        return (
            Z_COORDINATE_TOP_SIDE_OF_CARRIER
            - self._distance_below_top_side_of_carrier_to_consider_as_not_touching_floor
        )
