"""This module contains the class for the force and penetration recorder."""

import mujoco

from pet_physics.simulation.mujoco_lookup_helpers import get_contacts_of_geometry, get_geom_names_of_body
from pet_physics.simulation.physical_quantities.data_model.contact_force import ContactForce
from pet_physics.simulation.physical_quantities.history.force_history import ForceHistory
from pet_physics.simulation.physical_quantities.history.penetration_history import PenetrationHistory
from pet_physics.simulation.physical_quantities.quantity_names import QuantityName
from pet_physics.simulation.physical_quantities.recorders.base_recorder import BaseRecorder
from pet_physics.wrapper.data_extractor import DataExtractor
from pet_physics.wrapper.mj_contact_wrapper import MjContactWrapper


class ForcePenetrationRecorder(BaseRecorder):
    """This class is responsible for recording the forces and penetrations, respectively, that act in each simulation
    step on every body."""

    def __init__(self, mj_model: mujoco.MjModel, bodies: list[str], n_steps: int) -> None:
        """Initializes the force and penetration recorder.

        Args:
            n_steps (int): The number of simulation steps.
            mj_model (MjModel): The MuJoCo model.
            bodies (list[str]): The name of the bodies that are defined in the MuJoCo modelling XML file.
            collection_body_quantities (CollectionBodyQuantities): The collection of all body quantities that were
                recorded during the simulation.
        """
        super().__init__(mj_model=mj_model, bodies=bodies, n_steps=n_steps)

        self._detected_contacts = [None] * n_steps
        """The detected contacts in the simulation in every simulation step."""

        self._body_name_to_geom_names: dict[str, list[str]] = {
            body_name: get_geom_names_of_body(model=self._mj_model, body_name=body_name) for body_name in bodies
        }
        """A dictionary that maps body names to their corresponding geometry names."""

        self._force_history = ForceHistory(mj_model=self._mj_model, n_steps=n_steps)
        """The force history object that stores the force values during the simulation."""

        self._penetration_history = PenetrationHistory(mj_model=self._mj_model, n_steps=n_steps)
        """The penetration history object that stores the penetration values during the simulation."""

    def record(self, step_index: int, model: mujoco.MjModel, data: mujoco.MjData) -> None:
        """Records the force and the corresponding penetration in this simulation step.

        Args:
            step_index (int): The step index.
            model (MjModel): The MuJoCo model.
            data (MjData): The MuJoCo data object.
        """
        self.record_simulation_time(step_index, data)
        self._record_detected_contacts(step_index, data)

        detected_contacts_step = self._detected_contacts[step_index]
        for body_name in self.bodies:
            self._record_force_and_penetration_of_body(step_index, model, data, body_name, detected_contacts_step)

    def _record_detected_contacts(self, step_index: int, data: mujoco.MjData) -> None:
        """Records the detected contacts in this simulation step.

        Args:
            step_index (int): The step index.
            data (MjData): The MuJoCo data object.
        """
        self._detected_contacts[step_index] = DataExtractor.detected_contacts(data)

    def _record_force_and_penetration_of_body(
        self, step_index: int, model: mujoco.MjModel, data: mujoco.MjData, body_name: str, detected_contacts: list
    ) -> None:
        """Records the force and the corresponding penetration for a single body. This is done by filtering the
        detected contacts with respect to this body and then extract the contact forces and the corresponding
        penetration of this body.

        Args:
            step_index (int): The step index.
            model (MjModel): The MuJoCo model.
            data (MjData): The MuJoCo data object.
            body_name (str): The name of the body for that the forces and penetrations, respectively, are recorded.
            detected_contacts (list): The detected contacts in the current simulation step.
        """
        for geom in self._body_name_to_geom_names[body_name]:
            contacts_with_indices = get_contacts_of_geometry(model, detected_contacts, geom)
            for c_idx, c in contacts_with_indices:
                force_and_torque = DataExtractor.contact_force(model, data, c_idx)

                contact_force = ContactForce(
                    contact=MjContactWrapper(c, model),
                    value=force_and_torque[0:3],
                )

                self._force_history.track_value_of_body_in_step(
                    body_name=body_name, step_index=step_index, value=contact_force
                )

                self._penetration_history.track_value_of_body_in_step(
                    body_name=body_name, step_index=step_index, value=contact_force.penetration
                )

    def get_quantity_history_registrations(self) -> list[tuple[str, ForceHistory | PenetrationHistory]]:
        """Returns a list of tuples where each tuple contains the quantity name and its corresponding history object.

        This method is used to register the histories in the `CollectionBodyQuantities`.

        Returns:
            list[tuple[str, ForceHistory | PenetrationHistory]]: A list of tuples where each tuple contains the quantity
                name and its corresponding history object.
        """
        return [
            (QuantityName.FORCE, self._force_history),
            (QuantityName.PENETRATION, self._penetration_history),
        ]
