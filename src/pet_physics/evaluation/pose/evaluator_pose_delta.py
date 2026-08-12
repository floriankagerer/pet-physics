"""Evaluator that computes each body's position delta and maximum tiltedness."""

import numpy as np

from pet_physics.data_model.evaluation.pose.body_pose_delta import BodyPoseDelta
from pet_physics.data_model.evaluation.pose.result_evaluator_pose_delta import ResultEvaluatorPoseDelta
from pet_physics.data_model.physical_quantities.pose import Pose
from pet_physics.data_model.teleport import Teleport
from pet_physics.evaluation.base_evaluator import BaseEvaluator
from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities
from pet_physics.simulation.physical_quantities.quantity_names import QuantityName

NAME_EVALUATOR_POSE_DELTA = "pose_delta"
"""The name that is used for this evaluator."""


class EvaluatorPoseDelta(BaseEvaluator):
    """Determines position delta and maximum tiltedness for each body relative to its planned position.

    Attributes:
        cl_name: The name of this evaluator.
    """

    cl_name: str = NAME_EVALUATOR_POSE_DELTA

    def __init__(self, body_teleports: list[Teleport]) -> None:
        """Initializes the evaluator with the teleport definitions for each body.

        Args:
            body_teleports: The teleport objects providing planned positions for each body.
        """
        super().__init__()

        self._mapper_body_name_teleport = {teleport.name: teleport for teleport in body_teleports}
        """Maps the name of a body to its teleport object."""

    def _get_last_recorded_position(self, body_positions: list[np.ndarray | None]) -> np.ndarray:
        """Returns the last non-None recorded position for a body.

        Args:
            body_positions: The recorded positions, where not-yet-recorded entries are None.

        Returns:
            The most recently recorded position.
        """
        for i in range(len(body_positions)):
            last_recorded_position = body_positions[-(1 + i)]
            if last_recorded_position is not None:
                return last_recorded_position

    def _calculate_cleaned_position_delta(
        self, final_body_position: np.ndarray, planned_body_position: tuple[float, float, float]
    ) -> np.ndarray:
        """Calculates the delta between the final and planned positions, zeroing near-zero values.

        Near-zero values (absolute tolerance < 1e-3 m) are set to 0.0.

        Args:
            final_body_position: The body's last recorded position.
            planned_body_position: The body's planned position.

        Returns:
            The cleaned position delta with near-zero values set to 0.0.
        """
        delta_position = tuple(np.subtract(final_body_position, np.array(planned_body_position)))
        # set values that are close to zero, e.g., 1e-4, to 0.0
        cleaned_position_delta = np.where(np.isclose(delta_position, 0, atol=1e-3, rtol=0), 0.0, delta_position)

        return cleaned_position_delta

    def evaluate(self, collection_body_quantities: CollectionBodyQuantities) -> ResultEvaluatorPoseDelta:
        """Computes position delta and maximum tiltedness for all bodies in the simulation quantities.

        Args:
            collection_body_quantities: The collection of body quantities recorded during the simulation run.

        Returns:
            The position delta and tiltedness per body.
        """
        pose_history = collection_body_quantities.get_quantity_history(QuantityName.POSE)
        result_pose_delta = ResultEvaluatorPoseDelta()

        for body_name, body_pose_history in pose_history.body_name_with_values():
            body_pose_history: list[Pose]

            body_positions = [pose.pos for pose in body_pose_history]
            body_angles_with_z_axis = [pose.angle_with_z_axis for pose in body_pose_history]

            final_body_position = self._get_last_recorded_position(body_positions)
            planned_body_position = self._mapper_body_name_teleport.get(body_name).target_position
            # calculate the position delta
            cleaned_delta_position = self._calculate_cleaned_position_delta(final_body_position, planned_body_position)

            result_pose_delta.add(BodyPoseDelta(body_name, cleaned_delta_position, max(body_angles_with_z_axis)))

        return result_pose_delta
