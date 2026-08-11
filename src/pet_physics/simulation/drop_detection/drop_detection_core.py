"""Core functions to detect whether a box has fallen off the pallet during the simulation."""

import numpy as np

from pet_physics.constants import Z_COORDINATE_TOP_SIDE_OF_CARRIER


def is_z_coordinate_of_center_of_mass_below_top_side_of_carrier(
    position_center_of_mass: np.ndarray, z_coordinate_top_side_of_carrier: float = Z_COORDINATE_TOP_SIDE_OF_CARRIER
) -> bool:
    """Evaluates whether the z-coordinate of a body's center of mass is below the top side of the carrier.

    Note that the origin of the coordinate system is on top of the carrier, i.e., every z-coordinate that is smaller
    than this value means that the body is below the top side of the carrier, and, consequently, fell off the carrier.

    Args:
        position_center_of_mass: The position of the center of mass of the body.

    Returns:
        `True` if the z-coordinate of the body's center of mass is below the top side of the carrier, `False`
            otherwise.
    """

    _, _, z_center_of_mass = position_center_of_mass

    return z_center_of_mass < z_coordinate_top_side_of_carrier


def is_body_bottom_side_below_z_coordinate_that_defines_floor_contact(
    position_center_of_mass: np.ndarray, oriented_size: np.ndarray, z_coordinate_defining_floor_contact: float
) -> bool:
    """Evaluates whether the body's bottom side is below the z-coordinate that defines floor contact.

    Args:
        position_center_of_mass: The position of the center of mass of the body.
        oriented_size: The size of the body oriented according to its current rotation. Note that in MuJoCo, the size
            of a body is defined as the half-size.
        z_coordinate_defining_floor_contact: The z-coordinate that defines whether a body is considered as touching
            the floor. This value is typically calculated as the z-coordinate of the top side of the carrier minus
            a certain threshold.

    Returns:
        `True` if the body's bottom side is below the z-coordinate that defines floor contact, `False` otherwise.
    """
    _, _, z_center_of_mass = position_center_of_mass
    _, _, body_half_size_z = oriented_size

    z_coord_bottom_side = z_center_of_mass - body_half_size_z

    return z_coord_bottom_side < z_coordinate_defining_floor_contact
