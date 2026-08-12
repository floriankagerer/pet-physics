"""Contains an evaluator that checks whether a box has fallen off the pallet during the simulation."""

from pet_physics.data_model.evaluation.pose.result_evaluator_box_drop import ResultEvaluatorBoxDrop
from pet_physics.evaluation.base_evaluator import BaseEvaluator
from pet_physics.simulation.drop_detection.dropped_body_during_simulation_detector import (
    DroppedBodyDuringSimulationDetector,
)
from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities
from pet_physics.simulation.physical_quantities.quantity_names import QuantityName
from pet_physics.type_alias_definition import Size3d

NAME_EVALUATOR_BOX_DROP = "box_drop"
"""The name that is used for this evaluator."""


class EvaluatorBoxDrop(BaseEvaluator):
    """Evaluates whether any body has fallen off the pallet during the simulation.

    Attributes:
        cl_name: The name of this evaluator.
    """

    cl_name: str = NAME_EVALUATOR_BOX_DROP

    def __init__(self, body_name_to_size_mapping: dict[str, Size3d] | None = None) -> None:
        """Initializes the evaluator with an optional body-name-to-size mapping.

        Args:
            body_name_to_size_mapping: The dimensions of the boxes in the simulation, keyed by their MJCF body names.
        """

        super().__init__()

        self._body_name_to_size_mapping: dict[str, Size3d] | None = body_name_to_size_mapping
        """Contains the body names and keys and their sizes are the corresponding values."""

        self._dropped_body_during_simulation_detector = DroppedBodyDuringSimulationDetector()
        """Detects whether a body has fallen off the pallet during the simulation."""

    @property
    def body_name_to_size_mapping(self) -> dict[str, Size3d]:
        """The body name to size mapping."""
        if self._body_name_to_size_mapping is None:
            raise RuntimeError("The body name to size mapping is not set. Please set it before using this method.")

        return self._body_name_to_size_mapping

    @body_name_to_size_mapping.setter
    def body_name_to_size_mapping(self, value: dict[str, Size3d]) -> None:
        """Sets the body-name-to-size mapping.

        Args:
            value: The new mapping to set.
        """
        self._body_name_to_size_mapping = value

    def evaluate(self, collection_body_quantities: CollectionBodyQuantities) -> ResultEvaluatorBoxDrop:
        """Evaluates which bodies have fallen off the pallet during the simulation.

        Args:
            collection_body_quantities: The collection of body quantities recorded during the simulation run.

        Returns:
            The result containing all detected dropped bodies.
        """

        pose_history = collection_body_quantities.get_quantity_history(QuantityName.POSE)

        dropped_boxes = self._dropped_body_during_simulation_detector.detect(
            body_name_to_size_mapping=self.body_name_to_size_mapping, pose_history=pose_history
        )

        result_evaluator_box_drop = ResultEvaluatorBoxDrop(dropped_boxes=dropped_boxes)

        return result_evaluator_box_drop
