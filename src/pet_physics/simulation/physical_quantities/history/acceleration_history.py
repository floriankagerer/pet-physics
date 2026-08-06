"""This module contains the `AccelerationHistory` class, which tracks the history of accelerations of bodies during a
MuJoCo simulation."""

import numpy as np

from pet_physics.simulation.physical_quantities.data_model.acceleration import Acceleration
from pet_physics.simulation.physical_quantities.history.base_history import BaseHistory


class AccelerationHistory(BaseHistory):
    """This class stores the history of accelerations of all bodies during the simulation."""

    def _init_values(self) -> dict[str, list[Acceleration]]:
        """Initializes the dictionary that contains the tracked acceleration values for each body.

        Returns:
            A dictionary that contains the body name as key and a list of tracked acceleration values.
        """
        values: dict[str, list[Acceleration]] = {}

        for body_name in self._bodies:
            values[body_name] = [Acceleration(body_name) for _ in range(self._n_steps)]

        return values

    def _set_specific_value(self, body_name: str, step_index: int, value: np.ndarray) -> None:
        """Sets the specific tracked acceleration value for a body in a specific simulation step.

        Args:
            body_name: The name of the body.
            step_index: The step index.
            value: The acceleration value to be tracked as numpy array of length 6.
        """
        values_of_body: list[Acceleration] = self.get_values_of_body(body_name)

        values_of_body[step_index].value = value
