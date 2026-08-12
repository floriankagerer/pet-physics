"""This module represents the simulation time in MuJoCo."""

import numpy as np


class SimulationTime:
    """The simulation time in MuJoCo."""

    def __init__(self, n_steps: int) -> None:
        """The constructor.

        Args:
            n_steps: The number of simulation steps.
        """
        self._values = np.empty_like(None, shape=n_steps)

    def set_ith_value(self, i: int, value: float) -> None:
        """Sets the value for the i-th simulation step."""
        self._values[i] = value

    @property
    def values(self) -> np.ndarray:
        """The values of the simulation time in every step."""
        return self._values
