"""Contains a class that represents an item."""

from dataclasses import dataclass, fields

from pet_physics.data_model.base_data_model import BaseDataModel


@dataclass
class Item(BaseDataModel):
    """
    Represents an object that has to be packed and that is part of an order.

    Attributes
        id (str): The identifier of this item.
        article (str): The article name of this item.
        product_group (str): The product group this item belongs to.
        length_mm (int): The length of this item in millimeters.
        width_mm (int): The width of this item in millimeters.
        height_mm (int): The height of this item in millimeters.
        weight_kg (float): The weight of this item in kilograms.
        sequence (int): The position of this item within the item sequence.
    """

    id: str
    article: str
    product_group: str

    length_mm: int
    width_mm: int
    height_mm: int

    weight_kg: float

    sequence: int

    @property
    def color_identifier(self) -> str:
        """Returns the attribute's value that defines the color of this object."""
        return self.article

    def to_dict(self) -> dict[str, str | int | float]:
        """Converts the object to a dictionary."""
        item_to_dict = {}

        for item_field in fields(self):
            key = item_field.name
            item_to_dict[key] = getattr(self, key)

        return item_to_dict
