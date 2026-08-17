"""Data model describing a complete MuJoCo model configuration.

Defines the `ModelConfiguration` dataclass, which bundles the carrier body, the boxes placed on it, and their
corresponding teleports needed to build a MuJoCo model.
"""

from dataclasses import dataclass
from typing import Any

from dataclasses_json import dataclass_json

from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.serialization import to_dict
from pet_physics.data_model.teleport import Teleport
from pet_physics.type_alias_definition import Size3d


@dataclass_json
@dataclass
class ModelConfiguration:
    """A `ModelConfiguration` contains everything that is required to create a MuJoCo model. It contains the name of
    the model, the carrier, a list of boxes that are placed, the corresponding list of teleports, and whether the
    contacts with the floor are excluded from the collision check.

    Note that the `boxes` are stored as rigid bodies. This has the advantage that fewer records are required, since
    a body that is defined as soft body in MuJoCo creates multiple `<body>`-tags, depending on the amount of points.

    Attributes:
        model_name: The name of the model.
        carrier: The carrier, i.e., the object on that the boxes are placed.
        boxes: The boxes, stored as rigid body objects, that are placed.
        teleports: The teleport object for each box.
    """

    model_name: str
    carrier: Body
    boxes: list[Body]
    teleports: list[Teleport]

    def to_yaml(self) -> dict[str, Any]:
        as_yaml = {
            "carrier": to_dict(self.carrier),
            "boxes": [to_dict(b) for b in self.boxes],
            "teleports": [to_dict(t) for t in self.teleports],
        }
        return as_yaml

    @property
    def mass_of_boxes(self) -> float:
        """The total mass of all boxes in the model configuration."""
        total_mass = sum([box.geom.mass for box in self.boxes])
        return total_mass

    @property
    def mass_of_carrier(self) -> float:
        """The mass of the carrier in the model configuration."""
        return self.carrier.geom.mass

    @property
    def total_mass_of_carrier_and_boxes(self) -> float:
        """The total mass of the carrier and all boxes in the model configuration."""
        return self.mass_of_carrier + self.mass_of_boxes

    def get_box_names_to_sizes_mapping(self) -> dict[str, Size3d]:
        """Get a mapping from box names to their sizes.

        Returns:
            dict[str, Size3d]: A mapping from box names to their sizes as (length, width, height).
        """
        box_names_to_sizes_mapping: dict[str, Size3d] = {}

        for box in self.boxes:
            box_names_to_sizes_mapping[box.name] = box.geom.size

        return box_names_to_sizes_mapping
