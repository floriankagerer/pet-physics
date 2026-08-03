"""Wrapper module for MuJoCo visualization flag constants (`mjtVisFlag`)."""

from enum import IntEnum

import mujoco


class MjtVisFlag(IntEnum):
    """Indices into `mjvOption.flags` that enable or disable visualization of model or decoration elements.

    Url: https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjtvisflag

    Attributes:
        CONTACT_POINT: Contact points.
        CONTACT_FORCE: Contact force.
        TRANSPARENT: Make dynamic geoms more transparent.
    """

    CONTACT_POINT = mujoco.mjtVisFlag.mjVIS_CONTACTPOINT
    CONTACT_FORCE = mujoco.mjtVisFlag.mjVIS_CONTACTFORCE
    TRANSPARENT = mujoco.mjtVisFlag.mjVIS_TRANSPARENT
