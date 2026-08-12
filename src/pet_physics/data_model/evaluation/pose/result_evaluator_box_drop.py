"""The data model for the result of the `EvaluatorBoxDrop`."""

from typing import Self

from pet_physics.data_model.dropped_body import DroppedBody


class ResultEvaluatorBoxDrop:
    """The result of a `EvaluatorBoxDrop.evaluate`."""

    def __init__(self, dropped_boxes: list[DroppedBody] | None = None) -> None:
        """The constructor.

        Args:
            dropped_boxes: The list of dropped boxes. If `None`, an empty list is used.
        """
        self._dropped_boxes = dropped_boxes or []
        """The list of dropped boxes."""

    @property
    def timestep_first_drop(self) -> int | float | None:
        """The timestamp of the first drop. If no box has been dropped, `None` is returned."""
        if not self._dropped_boxes:
            return None

        return min(dropped_body.drop_timestamp for dropped_body in self._dropped_boxes)

    def to_dict(self) -> dict:
        """Converts this result to a dictionary representation.

        Returns:
            A mapping with dropped box names and the timestamp of the first drop.
        """
        as_dict = {
            "dropped_boxes": [str(dropped_body) for dropped_body in self._dropped_boxes],
            "timestep_first_drop": self.timestep_first_drop,
        }

        return as_dict

    def add(self, dropped_body: DroppedBody) -> Self:
        """Adds the given dropped body.

        Args:
            dropped_body: The dropped body that is added.

        Returns:
            This instance with the added dropped body.
        """
        self._dropped_boxes.append(dropped_body)

        return self
