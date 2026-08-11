"""Evaluator that computes the maximum acceleration of each body in a simulation run."""

from pet_physics.data_model.evaluation.acceleration.body_max_acceleration import BodyMaxAcceleration
from pet_physics.data_model.evaluation.acceleration.result_evaluator_max_acceleration import (
    ResultEvaluatorMaxAcceleration,
)
from pet_physics.evaluation.base_evaluator import BaseEvaluator
from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities
from pet_physics.simulation.physical_quantities.data_model.acceleration import Acceleration
from pet_physics.simulation.physical_quantities.quantity_names import QuantityName

NAME_EVALUATOR_MAX_ACCELERATION = "max_acceleration"
"""The name that is used for this evaluator."""


class EvaluatorMaxAcceleration(BaseEvaluator):
    """Determines the maximum linear and angular acceleration for each simulated body.

    Attributes:
        cl_name: The name of this evaluator.
    """

    cl_name: str = NAME_EVALUATOR_MAX_ACCELERATION

    @staticmethod
    def evaluate(collection_body_quantities: CollectionBodyQuantities) -> ResultEvaluatorMaxAcceleration:
        """Computes the maximum acceleration for all bodies in the simulation quantities.

        Args:
            collection_body_quantities: The collection of body quantities recorded during the simulation run.

        Returns:
            The maximum linear and angular acceleration per body.
        """
        acceleration_history = collection_body_quantities.get_quantity_history(QuantityName.ACCELERATION)
        result_max_acceleration = ResultEvaluatorMaxAcceleration()

        for body_name, body_acceleration_history in acceleration_history.body_name_with_values():
            body_acceleration_history: list[Acceleration]

            norm_linear_accelerations = [
                acceleration.norm_linear_acceleration for acceleration in body_acceleration_history
            ]
            norm_angular_accelerations = [
                acceleration.norm_angular_acceleration for acceleration in body_acceleration_history
            ]

            result_max_acceleration.add(
                BodyMaxAcceleration(body_name, max(norm_linear_accelerations), max(norm_angular_accelerations))
            )

        return result_max_acceleration
