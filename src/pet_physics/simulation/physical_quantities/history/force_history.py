"""This module contains the `ForceHistory` class, which tracks the history of forces of bodies during a
MuJoCo simulation."""

from pet_physics.data_model.physical_quantities.body_forces import BodyForces
from pet_physics.data_model.physical_quantities.contact_force import ContactForce
from pet_physics.simulation.physical_quantities.history.base_history import BaseHistory


class ForceHistory(BaseHistory):
    """This class stores the history of forces of all bodies during the simulation."""

    def _init_values(self) -> dict[str, list[BodyForces]]:
        """Initializes the dictionary that contains the tracked forces for each body.

        Returns:
            A dictionary that contains the body name as key and a list of tracked body forces values.
        """
        values: dict[str, list[BodyForces]] = {}

        for body_name in self._bodies:
            geom_names_of_body = self._body_name_to_geom_names[body_name]
            values[body_name] = [BodyForces(body_name, geom_names_of_body) for _ in range(self._n_steps)]

        return values

    def _set_specific_value(self, body_name: str, step_index: int, value: ContactForce) -> None:
        """Sets the specific tracked force value for a body in a specific simulation step.

        Args:
            body_name: The name of the body.
            step_index: The step index.
            value: The force value to be tracked.
        """
        values_of_body: list[BodyForces] = self.get_values_of_body(body_name)

        values_of_body[step_index].add_contact_force(value)
