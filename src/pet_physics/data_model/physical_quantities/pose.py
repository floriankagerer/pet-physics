"""This module tracks a body's pose value during the simulation."""

from copy import deepcopy

import numpy as np

from pet_physics.constants import UNIT_NORMAL_Z_AXIS
from pet_physics.utils.quaternion_utils import rotate_vector_by_quaternion


class Pose:
    """Wraps the position and the quaternion from MuJoCo's `MjData` object. This class provides properties to
    easily access the position of a body and its tiltedness.

    Note that whenever the value of the position or quaternion is set, a deepcopy of the given `np.ndarray` is set,
    since otherwise issues occur, similiarly to the contacts.
    """

    def __init__(self, body_name: str, pos: np.ndarray | None = None, quat: np.ndarray | None = None) -> None:
        """The constructor of this class.

        Args:
            body_name: The name of the body as it is specified in the MJCF.
            pos: The value of a body's **position** as it is stored in the data object of MuJoCo.
            quat: The value of a body's **quaternion** as it is stored in the data object of MuJoCo.
        """

        self._body_name = body_name
        """The name of the body as it is specified in the MJCF."""
        self._pos = deepcopy(pos) or None
        """The value of a body's **position** as it is stored in the data object of MuJoCo."""
        self._quaternion = deepcopy(quat) or np.zeros(4)
        """The value of a body's **quaternion** as it is stored in the data object of MuJoCo."""

    @property
    def pos(self) -> np.ndarray:
        """The value of a body's **position** as it is stored in the data object of MuJoCo."""
        return self._pos

    @pos.setter
    def pos(self, value: np.ndarray) -> None:
        self._pos = deepcopy(value)

    @property
    def quat(self) -> np.ndarray:
        """The value of a body's **quaternion** as it is stored in the data object of MuJoCo."""
        return self._quaternion

    @quat.setter
    def quat(self, value: np.ndarray) -> None:
        self._quaternion = deepcopy(value)

    @property
    def distance_to_origin(self) -> float:
        """The distance of a body's position to the origin."""
        if self.pos is None:
            return 0.0

        return np.linalg.norm(self.pos)

    @property
    def rotated_unit_normal_z(self) -> np.ndarray:
        """Returns the rotated unit normal of the z-axis that is defined by the quaternion of this pose."""
        return rotate_vector_by_quaternion(UNIT_NORMAL_Z_AXIS, self.quat, normalize_vectors=True)

    @property
    def angle_with_z_axis(self) -> float:
        """Calculates the angle between the z-axis and the roated unit normal in z-direction of this pose."""
        unit_normal_z = np.array(UNIT_NORMAL_Z_AXIS, dtype=float)
        cos_alpha_rad = np.dot(unit_normal_z, self.rotated_unit_normal_z)

        cos_alpha_rad = np.clip(cos_alpha_rad, -1, 1)
        alpha_rad = np.arccos(cos_alpha_rad)

        return np.degrees(alpha_rad).round(1)
