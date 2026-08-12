"""This module tracks a body's acceleration value during the simulation."""

from copy import deepcopy

import numpy as np


class Acceleration:
    """Wraps the acceleration that is extracted from MuJoCos `MjData` object. This class provides properties to
    easily access the linear acceleration, the angular acceleration, and the corresponding norm values.

    Note that whenever the acceleration `value` is set, a deepcopy of the given `np.ndarray` is set, since otherwise
    issues occur, similarly to the contacts.
    """

    def __init__(self, body_name: str, value: np.ndarray | None = None) -> None:
        """The constructor of this class.

        Args:
            body_name: The name of the body as it is specified in the MJCF.
            value: The value of a body's acceleration as it is stored in the data object of MuJoCo.
        """

        self._body_name = body_name
        """The name of the body as it is specified in the MJCF."""
        self._value = value or np.zeros(6)
        """The value of a body's acceleration as it is stored in the data object of MuJoCo."""

    @property
    def value(self) -> np.ndarray:
        """The value of a body's acceleration as it is stored in the data object of MuJoCo."""
        return self._value

    @value.setter
    def value(self, value: np.ndarray) -> None:
        self._value = deepcopy(value)

    @property
    def linear_acceleration(self) -> np.ndarray:
        """The linear acceleration."""
        return self._value[:3]

    @property
    def angular_acceleration(self) -> np.ndarray:
        """The angular acceleration."""
        return self._value[3:]

    @property
    def norm_linear_acceleration(self) -> float:
        """The norm of the linear acceleration vector."""
        return np.linalg.norm(self.linear_acceleration)

    @property
    def norm_angular_acceleration(self) -> float:
        """The norm of the angular acceleration vector."""
        return np.linalg.norm(self.angular_acceleration)
