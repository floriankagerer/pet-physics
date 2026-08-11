"""Contains a class that represents an action, i.e., a packing instruction."""

from dataclasses import dataclass, fields
from typing import Self

from pet_physics.data_model.packing.base_data_model import BaseDataModel
from pet_physics.data_model.packing.item import Item
from pet_physics.data_model.packing.orientation import Orientation
from pet_physics.data_model.packing.position_3d import Position3D


@dataclass
class Action(BaseDataModel):
    """
    An action represents which item is placed, in which location, and in which orientation.

    Attributes:
        item (Item): The item that is placed with this action.
        orientation (Orientation): The orientation of the item.
        flb_coordinates (Position3D): The position of the item of this action.
    """

    item: Item
    orientation: Orientation
    flb_coordinates: Position3D

    @classmethod
    def from_dict(cls, serialized: dict[str, str | list[dict]]) -> Self:
        """Deserialize dictionary into dataclass instance."""
        init_kwargs = {}
        for f in fields(cls):
            key = f.name

            if key == "item":
                init_kwargs[key] = Item.from_dict(serialized[key])

            elif key == "flb_coordinates":
                init_kwargs[key] = Position3D(*serialized[key])

            else:
                init_kwargs[key] = serialized[key]

        return cls(**init_kwargs)

    def to_dict(self) -> dict:
        """Converts the object to a dictionary."""
        as_dict = {
            "item": self.item.to_dict(),
            "orientation": self.orientation,
            "flb_coordinates": list(self.flb_coordinates.xyz),
        }
        return as_dict
