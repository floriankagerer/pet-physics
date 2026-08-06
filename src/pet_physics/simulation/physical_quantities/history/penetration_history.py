"""This module contains the `PenetrationHistory` class, which tracks the history of penetration of bodies during a
MuJoCo simulation."""

from pet_physics.simulation.physical_quantities.data_model.penetration import Penetration
from pet_physics.simulation.physical_quantities.history.base_history import BaseHistory


class PenetrationHistory(BaseHistory):
    """This class stores the history of penetration of all bodies during the simulation."""

    def _init_values(self) -> dict[str, list[Penetration]]:
        """Initializes the dictionary that contains the tracked penetration values for each body.

        Returns:
            A dictionary that contains the body name as key and a list of tracked penetration values.
        """
        values: dict[str, list[Penetration]] = {}

        for body_name in self._bodies:
            values[body_name] = [Penetration(body_name) for _ in range(self._n_steps)]

        return values

    def _set_specific_value(self, body_name: str, step_index: int, value: float) -> None:
        """Sets the specific tracked penetration value for a body in a specific simulation step.

        Args:
            body_name: The name of the body.
            step_index: The step index.
            value: The penetration value to be tracked.
        """
        values_of_body: list[Penetration] = self.get_values_of_body(body_name)

        values_of_body[step_index].update_value(value)
