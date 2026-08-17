"""Result data model for the maximum top contact force evaluator."""

from typing import Self

import structlog

from pet_physics.data_model.evaluation.forces.body_max_contact_force_top import BodyMaxContactForceTop

logger = structlog.get_logger(__name__)


class ResultEvaluatorMaxContactForceTop:
    """Stores maximum top contact force results for all bodies produced by EvaluatorMaxContactForceTop."""

    def __init__(self) -> None:
        self._records: dict[str, BodyMaxContactForceTop] = {}
        """The records of the maximum top contact forces for each body."""

    def to_dict(self) -> dict:
        """Converts this result to a dictionary representation.

        Returns:
            A mapping of body name to its maximum top contact force value.
        """
        return {body_name: value.max_contact_force_top for body_name, value in self._records.items()}

    def add(self, record: BodyMaxContactForceTop) -> Self:
        """Adds a body's maximum contact force record to this result.

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

    def values(self) -> list[BodyMaxContactForceTop]:
        """Returns the maximum top contact force records for all bodies.

        Returns:
            The list of per-body contact force records.
        """
        return list(self._records.values())
