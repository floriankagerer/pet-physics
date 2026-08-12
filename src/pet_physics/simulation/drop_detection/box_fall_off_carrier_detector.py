"""Drop detector that detects whether a box has fallen off the carrier based on the position of its center of mass and
its oriented size."""

import numpy as np

from pet_physics.simulation.drop_detection.base_drop_detector import BaseDropDetector
from pet_physics.simulation.drop_detection.drop_detection_core import (
    is_body_bottom_side_below_z_coordinate_that_defines_floor_contact,
    is_z_coordinate_of_center_of_mass_below_top_side_of_carrier,
)


class BoxFallOffCarrierDetector(BaseDropDetector):
    """This class is responsible to detect whether a box has fallen off the pallet, based on the position of its center
    of mass and its oriented size.

    A box is considered as dropped if
    - the body's center of mass is below the top side of the carrier, or
    - the body's bottom side is at least some distance below the top side of the carrier.

    Note that the *oriented size* represents the size of the axis-aligned bounding box (AABB) of the body, where
    the AABB is the smallest bounding box that contains the (rotated) body and is aligned with the coordinate axes.
    """

    def detect(self, position_center_of_mass: np.ndarray, oriented_size: np.ndarray) -> bool:
        """Detects whether a box has fallen off the carrier based on its position and oriented size.

        Args:
            position_center_of_mass: The position of the center of mass of the body.
            oriented_size: The size of the body oriented according to its current rotation. Note that in MuJoCo,
                the size of a body is defined as the half-size.

        Returns:
            `True` if we think that the box fell of the carrier, `False` otherwise.
        """

        return is_z_coordinate_of_center_of_mass_below_top_side_of_carrier(
            position_center_of_mass=position_center_of_mass
        ) or is_body_bottom_side_below_z_coordinate_that_defines_floor_contact(
            position_center_of_mass=position_center_of_mass,
            oriented_size=oriented_size,
            z_coordinate_defining_floor_contact=self.z_coordinate_defining_floor_contact,
        )
