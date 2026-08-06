"""This module contains the class for the acceleration recorder."""

import mujoco
import numpy as np

from pet_physics.simulation.mujoco_lookup_helpers import get_joint_start_address_of_body
from pet_physics.simulation.physical_quantities.history.acceleration_history import AccelerationHistory
from pet_physics.simulation.physical_quantities.quantity_names import QuantityName
from pet_physics.simulation.physical_quantities.recorders.base_recorder import BaseRecorder
from pet_physics.wrapper.data_extractor import DataExtractor


class AccelerationRecorder(BaseRecorder):
    """This class is responsible for recording the acceleration of every body in each simulation step."""

    def __init__(self, mj_model: mujoco.MjModel, bodies: list[str], n_steps: int) -> None:
        """Initializes the acceleration recorder.

        Args:
            n_steps: The number of simulation steps.
            mj_model: The MuJoCo model.
            bodies: The name of the bodies that are defined in the MuJoCo modelling XML file.
        """
        super().__init__(mj_model=mj_model, bodies=bodies, n_steps=n_steps)

        self._joint_start_address = {
            body_name: get_joint_start_address_of_body(self._mj_model, body_name) for body_name in bodies
        }
        """A dictionary that contains the body name as key and its corresponding joint start address in the data."""

        self._acceleration_history = AccelerationHistory(mj_model=self._mj_model, n_steps=n_steps)
        """Stores the history of accelerations of bodies during the simulation."""

    def record(self, step_index: int, model: mujoco.MjModel, data: mujoco.MjData) -> None:
        """Records the acceleration of every body in this simulation step. Firstly, the overall accelerations
        are extracted for this step and secondly, the values for each body are obtained.

        Args:
            step_index: The step index.
            model: The MuJoCo model.
            data: The MuJoCo data object.
        """
        self.record_simulation_time(step_index, data)
        acceleration_data = DataExtractor.acceleration(data)
        for body_name in self.bodies:
            self._record_acceleration_of_body(step_index, acceleration_data, body_name)

    def _record_acceleration_of_body(self, step_index: int, acceleration_data: np.ndarray, body_name: str) -> None:
        """Records the acceleration of a single body.

        Args:
            step_index: The step index.
            acceleration_data: The array that contains the accelerations of all bodies.
            body_name: The name of the body for that the acceleration is recorded.
        """
        acceleration_value_as_array = self._get_acceleration_of_body(acceleration_data, body_name)
        self._acceleration_history.track_value_of_body_in_step(
            body_name=body_name, step_index=step_index, value=acceleration_value_as_array
        )

    def _get_acceleration_of_body(self, acceleration_data: np.ndarray, body_name: str) -> np.ndarray:
        """Returns the actual value of the body's acceleration.

        Args:
            acceleration_data: The array that contains the accelerations of all bodies.
            body_name: The name of the body for that the forces and penetrations, respectively, are recorded.

        Returns:
            The values of the body's acceleration.
        """
        joint_start_adress = self._joint_start_address.get(body_name)
        body_acceleration = acceleration_data[joint_start_adress : joint_start_adress + 6]

        return body_acceleration

    def get_quantity_history_registrations(self) -> list[tuple[str, AccelerationHistory]]:
        """Returns a list of tuples where each tuple contains the quantity name and its corresponding history object.

        This method is used to register the histories in the `CollectionBodyQuantities`.

        Returns:
            A list of tuples where each tuple contains the quantity name and its
                corresponding history object.
        """
        return [(QuantityName.ACCELERATION, self._acceleration_history)]
