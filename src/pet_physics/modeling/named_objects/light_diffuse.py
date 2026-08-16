from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.light import Light


@dataclass
class LightDiffuse(Light):
    """Class to represent a diffuse light in a MuJoCo model.
    This object belongs to the `worldbody` part of a model."""

    def __init__(self) -> None:
        super().__init__((0.5, 0.5, 0.5), pos=(0, 0, 10), dir=(0, 0, -1))
