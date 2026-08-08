"""Result data model for the pose delta evaluator."""

from typing import Self

import numpy as np
import structlog

from pet_physics.data_model.evaluation.pose.body_pose_delta import BodyPoseDelta
from pet_physics.data_model.evaluation.pose.threshold_pose_delta import ThresholdPoseDelta
from pet_physics.data_model.serialization import to_dict

logger = structlog.get_logger(__name__)


class ResultEvaluatorPoseDelta:
    """Stores pose delta results for all bodies produced by EvaluatorPoseDelta."""

    def __init__(self) -> None:
        self._records: dict[str, BodyPoseDelta] = {}
        """The records of the pose delta for each body."""

    def to_dict(self) -> dict:
        """Converts this result to a dictionary representation.

        Returns:
            A mapping of body name to its serialized pose delta record.
        """
        as_dict = {}
        for body_name, body_pose_delta in self._records.items():
            dict_body_pose_delta = to_dict(body_pose_delta)
            _ = dict_body_pose_delta.pop("name", None)

            as_dict[body_name] = dict_body_pose_delta

        return as_dict

    def add(self, record: BodyPoseDelta) -> Self:
        """Adds the given record.

        Args:
            record: The record that is added.

        Returns:
            The current instance.
        """
        name = record.name
        if name in self._records:
            logger.warning(f"overwrite the record for '{name}'")

        self._records.update({name: record})

        return self

    def values(self) -> list[BodyPoseDelta]:
        """Returns the pose delta records for all bodies.

        Returns:
            The list of per-body pose delta records.
        """
        return list(self._records.values())

    def are_records_within_threshold(self, threshold: ThresholdPoseDelta) -> tuple[bool, dict[str, str]]:
        """Checks whether all body pose delta records are within the given threshold.

        Args:
            threshold: The threshold used for the check.

        Returns:
            A tuple where the first element indicates whether all bodies satisfy all pose delta criteria, and the second
                element maps violating body names to their violation messages.
        """
        # init return values
        bodies_satisfy_criteria = []
        additional_information = {}

        criteria = ["x", "y", "z", "tiltedness"]
        thresholds = [
            threshold.max_x_delta_m,
            threshold.max_y_delta_m,
            threshold.max_z_delta_m,
            threshold.max_tiltedness_degrees,
        ]

        for body_name, record in self._records.items():
            body_criteria_satisfied = []
            body_msg_violations = []
            abs_position_delta = np.abs(record.final_position_delta)

            values: list = abs_position_delta.tolist() + [record.max_body_tiltedness]

            for criterion, criterion_value, criterion_threshold in zip(criteria, values, thresholds):
                criterion_satisfied = criterion_value <= criterion_threshold
                body_criteria_satisfied.append(criterion_satisfied)

                if not criterion_satisfied:
                    msg = f"{criterion} violated ({criterion_value}>{criterion_threshold})"
                    body_msg_violations.append(msg)

            # check whether all criteria are satisfied for this body
            are_all_criteria_satisfied_body = all(body_criteria_satisfied)

            bodies_satisfy_criteria.append(are_all_criteria_satisfied_body)

            if not are_all_criteria_satisfied_body:
                additional_information[body_name] = ";".join(body_msg_violations)

        return all(bodies_satisfy_criteria), additional_information
