"""Result data model for the maximum acceleration evaluator."""

from typing import Self

import structlog

from pet_physics.data_model.evaluation.acceleration.body_max_acceleration import BodyMaxAcceleration
from pet_physics.data_model.serialization import to_dict

logger = structlog.get_logger(__name__)


class ResultEvaluatorMaxAcceleration:
    """Stores maximum acceleration results for all bodies produced by EvaluatorMaxAcceleration."""

    def __init__(self) -> None:
        self._records: dict[str, BodyMaxAcceleration] = {}
        """The records of the accelerations for each body."""

    def to_dict(self) -> dict:
        """Converts this result to a dictionary representation.

        Returns:
            A mapping of body name to its serialized max acceleration record.
        """
        return {key: to_dict(value) for key, value in self._records.items()}

    def add(self, record: BodyMaxAcceleration) -> Self:
        """Adds a body's maximum acceleration record to this result.

        Args:
            record: The record to add.

        Returns:
            This instance with the record added.
        """
        name = record.name
        if name in self._records:
            logger.warning(f"overwrite the record for '{name}'")

        self._records.update({name: record})

        return self

    def values(self) -> list[BodyMaxAcceleration]:
        """Returns the maximum acceleration records for all bodies.

        Returns:
            The list of per-body acceleration records.
        """
        return list(self._records.values())

    @property
    def maximal_value_linear_acceleration(self) -> float:
        """The maximal value of the linear acceleration throughout all bodies."""
        values_linear_acceleration = [body_acc.max_linear_acceleration for body_acc in self.values()]
        return max(values_linear_acceleration)

    @property
    def maximal_value_angular_acceleration(self) -> float:
        """The maximal value of the angular acceleration throughout all bodies."""
        values_angular_acceleration = [body_acc.max_angular_acceleration for body_acc in self.values()]
        return max(values_angular_acceleration)
