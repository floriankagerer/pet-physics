"""This module contains the `PoseHistory` class, which tracks the history of poses of bodies during a MuJoCo
simulation."""

import numpy as np

from pet_physics.data_model.physical_quantities.pose import Pose
from pet_physics.simulation.physical_quantities.history.base_history import BaseHistory


class PoseHistory(BaseHistory):
    """This class stores the history of poses of all bodies during the simulation."""

    def _init_values(self) -> dict[str, list[Pose]]:
        """Initializes the dictionary that contains the tracked pose values for each body.

        Returns:
            A dictionary that contains the body name as key and a list of tracked pose values.
        """
        values: dict[str, list[Pose]] = {}

        for body_name in self._bodies:
            values[body_name] = [Pose(body_name) for _ in range(self._n_steps)]

        return values

    def _set_specific_value(self, body_name: str, step_index: int, value: tuple[np.ndarray, np.ndarray]) -> None:
        """Sets the specific tracked pose value for a body in a specific simulation step.

        Args:
            body_name: The name of the body.
            step_index: The step index.
            value: The pose value to be tracked as a tuple of two numpy arrays, representing position and orientation.
        """
        body_position, body_quaternion = value

        values_of_body: list[Pose] = self.get_values_of_body(body_name)

        values_of_body[step_index].pos = body_position
        values_of_body[step_index].quat = body_quaternion
