"""This module contains the class for the number of contacts recorder."""

import mujoco

from pet_physics.simulation.physical_quantities.quantity_names import QuantityName
from pet_physics.simulation.physical_quantities.recorders.base_recorder import BaseRecorder
from pet_physics.wrapper.data_extractor import DataExtractor


class NContactsRecorder(BaseRecorder):
    """This class is responsible for recording the number of contacts during the simulation."""

    def __init__(self, mj_model: mujoco.MjModel, bodies: list[str], n_steps: int) -> None:
        """Initializes the number of detected contacts recorder.

        Args:
            n_steps (int): The number of simulation steps.
            mj_model (MjModel): The MuJoCo model.
            bodies (list[str]): The name of the bodies that are defined in the MuJoCo modelling XML file.
            collection_body_quantities (CollectionBodyQuantities): The collection of all body quantities that were
                recorded during the simulation.
        """
        super().__init__(mj_model=mj_model, bodies=bodies, n_steps=n_steps)

        self._n_contacts_history = [None] * n_steps
        """Stores the history of number of contacts during the simulation."""

    @property
    def records_n_contacts(self) -> list[int]:
        """The number of detected contacts in the simulation in every simulation step."""
        return [record for record in self._n_contacts_history if record is not None]

    def record(self, step_index: int, model: mujoco.MjModel, data: mujoco.MjData) -> None:
        """Records the number of detected contacts in this simulation step.

        Args:
            step_index (int): The step index.
            model (MjModel): The MuJoCo model.
            data (MjData): The MuJoCo data object.
        """
        self.record_simulation_time(step_index, data)
        self._record_n_detected_contacts(step_index, data)

    def _record_n_detected_contacts(self, step_index: int, data: mujoco.MjData) -> None:
        """Records the number of detected contacts in this simulation step.

        Args:
            step_index (int): The step index.
            data (MjData): The MuJoCo data object.
        """
        self._n_contacts_history[step_index] = DataExtractor.number_contacts(data)

    def get_quantity_history_registrations(self) -> list[tuple[str, list[int]]]:
        """Returns a list of tuples where each tuple contains the quantity name and its corresponding history object.

        This method is used to register the histories in the `CollectionBodyQuantities`.

        Returns:
            list[tuple[str, BaseHistory]]: A list of tuples where each tuple contains the quantity name and its
                corresponding history object.
        """
        return [
            (QuantityName.N_CONTACTS, self._n_contacts_history),
        ]
