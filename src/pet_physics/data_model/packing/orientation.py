"""Represents the orientation of an item."""

from enum import IntEnum

from pet_physics.data_model.packing.item import Item
from pet_physics.data_model.type_alias import Size3d


class Orientation(IntEnum):
    """
    Defines the orientation of an item.

    Attributes:
        LWH (int): The item's original orientation.
        WLH (int): Swap length and width.
    """

    LWH = 0
    WLH = 1

    def get_item_size(self, item: Item) -> Size3d:
        """
        Returns the size of an item with respect to the provided orientation.

        Args:
            item (Item): The item for that the size with respect to the orientation is returned.

        Returns:
            tuple[int,int,int]: The length, width, and height of the item if it has the provided orientation.
        """
        if self is Orientation.LWH:
            size = item.length_mm, item.width_mm, item.height_mm

        elif self is Orientation.WLH:
            size = item.width_mm, item.length_mm, item.height_mm

        else:
            raise NotImplementedError(f"'get_item_size' is not implented for '{self}'")

        return size
