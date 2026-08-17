"""Evaluator that computes the maximum top contact force for each body in a simulation run."""

from pet_physics.data_model.evaluation.forces.body_max_contact_force_top import BodyMaxContactForceTop
from pet_physics.data_model.evaluation.forces.result_evaluator_max_contact_force_top import (
    ResultEvaluatorMaxContactForceTop,
)

from pet_physics.data_model.physical_quantities.body_forces import BodyForces
from pet_physics.evaluation.base_evaluator import BaseEvaluator
from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities
from pet_physics.simulation.physical_quantities.quantity_names import QuantityName

NAME_EVALUATOR_MAX_CONTACT_FORCE_TOP = "max_contact_force_top"
"""The name that is used for this evaluator."""


class EvaluatorMaxContactForceTop(BaseEvaluator):
    """Determines the maximum z-direction contact force acting on top of each simulated body.

    Attributes:
        cl_name: The name of this evaluator.
    """

    cl_name: str = NAME_EVALUATOR_MAX_CONTACT_FORCE_TOP

    @staticmethod
    def evaluate(collection_body_quantities: CollectionBodyQuantities) -> ResultEvaluatorMaxContactForceTop:
        """Computes the maximum top contact force for all bodies in the simulation quantities.

        Args:
            collection_body_quantities: The collection of body quantities recorded during the simulation run.

        Returns:
            The maximum top contact force per body.
        """
        force_history = collection_body_quantities.get_quantity_history(QuantityName.FORCE)
        result_max_contact_force_top = ResultEvaluatorMaxContactForceTop()

        for body_name, body_force_history in force_history.body_name_with_values():
            body_force_history: list[BodyForces]

            body_contact_forces_top = [force.sum_contact_forces_z_top for force in body_force_history]
            result_max_contact_force_top.add(BodyMaxContactForceTop(body_name, max(body_contact_forces_top)))

        return result_max_contact_force_top
