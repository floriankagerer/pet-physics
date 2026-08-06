"""This module contains the class for the pose recorder."""

import mujoco

from pet_physics.simulation.mujoco_lookup_helpers import get_body_id
from pet_physics.simulation.physical_quantities.history.pose_history import PoseHistory
from pet_physics.simulation.physical_quantities.quantity_names import QuantityName
from pet_physics.simulation.physical_quantities.recorders.base_recorder import BaseRecorder


class PoseRecorder(BaseRecorder):
    """This class is responsible for recording the pose of every body in each simulation step."""

    def __init__(self, mj_model: mujoco.MjModel, bodies: list[str], n_steps: int) -> None:
        """Initializes the pose recorder.

        Args:
            n_steps (int): The number of simulation steps.
            mj_model (MjModel): The MuJoCo model.
            bodies (list[str]): The name of the bodies that are defined in the MuJoCo modelling XML file.
        """
        super().__init__(mj_model=mj_model, bodies=bodies, n_steps=n_steps)

        self._body_id_of = {body_name: get_body_id(self._mj_model, body_name) for body_name in bodies}
        """A dictionary that contains the body name as key and its corresponding body id in the data as value."""

        self._pose_history = PoseHistory(mj_model=self._mj_model, n_steps=n_steps)
        """Stores the history of poses of bodies during the simulation."""

    def record(self, step_index: int, model: mujoco.MjModel, data: mujoco.MjData) -> None:
        """Records the pose of every body in this simulation step.

        Args:
            step_index (int): The step index.
            model (MjModel): The MuJoCo model.
            data (MjData): The MuJoCo data object.
        """
        self.record_simulation_time(step_index, data)
        for body_name in self.bodies:
            self._record_pose_of_body(step_index, data, body_name)

    def _record_pose_of_body(self, step_index: int, data: mujoco.MjData, body_name: str) -> None:
        """Records the pose of a single body. We get the position by accessing `data.xpos[body_id]` as described in
        `BodyTeleporter` and the quaternion by accessing `data.xquat[body_id]`.

        Args:
            step_index (int): The step index.
            data (MjData): The MuJoCo data object.
            body_name (str): The name of the body for that the pose is recorded.
        """
        body_id = self._body_id_of[body_name]

        body_pos = data.xpos[body_id]
        body_quat = data.xquat[body_id]

        self._pose_history.track_value_of_body_in_step(
            body_name=body_name, step_index=step_index, value=(body_pos, body_quat)
        )

    def get_quantity_history_registrations(self) -> list[tuple[str, PoseHistory]]:
        """Returns a list of tuples where each tuple contains the quantity name and its corresponding history object.

        This method is used to register the histories in the `CollectionBodyQuantities`.

        Returns:
            list[tuple[str, PoseHistory]]: A list of tuples where each tuple contains the quantity name and its
                corresponding history object.
        """
        return [
            (QuantityName.POSE, self._pose_history),
        ]
