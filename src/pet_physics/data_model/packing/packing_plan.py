"""Represents a packing plan, i.e., actions which describe where, in which pose, and when to place an item."""

from dataclasses import dataclass, fields
from typing import Self

from pet_physics.data_model.packing.action import Action
from pet_physics.data_model.packing.base_data_model import BaseDataModel


@dataclass
class PackingPlan(BaseDataModel):
    """
    Represents a packing plan, i.e., actions which describe where, in which pose, and when to place an item.

    Attributes:
        id (str): The identifier of this packing plan.
        actions (list[Action]): The actions of this packing plan.
    """

    id: str
    actions: list[Action]

    @classmethod
    def from_dict(cls, serialized: dict[str, str | list[dict]]) -> Self:
        """Deserialize dictionary into dataclass instance."""
        init_kwargs = {}

        for f in fields(cls):
            key = f.name

            if key == "actions":
                action_sequence = [Action.from_dict(serialized_action) for serialized_action in serialized[key]]
                init_kwargs[key] = action_sequence

            else:
                init_kwargs[key] = serialized[key]

        return cls(**init_kwargs)

    def to_dict(self) -> dict:
        """Converts the object to a dictionary."""
        as_dict = {}

        for packing_plan_field in fields(self):
            key = packing_plan_field.name

            if key == "id":
                as_dict[key] = getattr(self, key)

            elif key == "actions":
                as_dict[key] = [action.to_dict() for action in self.actions]

        return as_dict
