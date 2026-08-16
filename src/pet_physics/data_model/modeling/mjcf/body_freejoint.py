"""Module that contains a class representing a freejoint body."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json

from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.modeling.mjcf.freejoint import Freejoint


@dataclass_json
@dataclass
class BodyFreejoint(Body):
    """Class to represent a body with its associated properties and components that has a free joint."""

    name: str
    pos: tuple[float, float, float]
    axisangle: tuple[int, int, int, int] | None = None

    def __init__(
        self,
        name: str,
        pos: tuple[float, float, float],
        axisangle: tuple[int, int, int, int] | None = None,
    ) -> None:
        super().__init__(name=name, pos=pos, axisangle=axisangle)
        self.add_child(Freejoint())


# Override the default from_dict
BodyFreejoint.to_dict = BodyFreejoint.custom_to_dict
# Override the default to_dict
BodyFreejoint.from_dict = BodyFreejoint.custom_from_dict
