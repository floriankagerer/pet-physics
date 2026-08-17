"""Contains the classes that represent the floor and its texture and material for a MuJoCo model."""

from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.modeling.mjcf.geom import Geom
from pet_physics.data_model.modeling.mjcf.material import Material
from pet_physics.data_model.modeling.mjcf.texture import Texture


@dataclass
class FloorTexture(Texture):
    """Class to represent the texture of a floor in a MuJoCo model.
    This object belongs to the `asset` part of a model."""

    def __init__(self) -> None:
        super().__init__(
            name="grid",
            type="2d",
            builtin="checker",
            rgb1=(0.1, 0.2, 0.3),
            rgb2=(0.2, 0.3, 0.4),
            width=300,
            height=300,
            mark="edge",
            markrgb=(0.2, 0.3, 0.4),
        )


class FloorMaterial(Material):
    """Class to represent the material of a floor in a MuJoCo model.
    This object belongs to the `asset` part of a model."""

    def __init__(self) -> None:
        super().__init__(
            name="grid",
            texture="grid",
            texrepeat="2 2",
            texuniform="true",
            reflectance=0.0,
        )


@dataclass
class Floor(Body):
    """Class to represent the floor in a MuJoCo model.
    This object belongs to the `worldbody` part of a model."""

    def __init__(self) -> None:
        geom = Geom(
            name="_floor.ground",
            type="plane",
            size=(0, 0, 0.05),
            material="grid",
            mass=None,
            rgba=None,
        )
        super().__init__(
            name="_floor",
            pos=(0, 0, -0.144),
        )
        self.add_child(geom)
