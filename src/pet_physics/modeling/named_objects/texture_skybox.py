from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.texture import Texture


@dataclass
class TextureSkybox(Texture):
    """Class to represent the texture for the skybox in a MuJoCo model.
    This object belongs to the `asset` part of a model.
    """

    def __init__(self) -> None:
        super().__init__(
            name="sky",
            type="skybox",
            builtin="flat",
            rgb1=(0.9, 0.9, 0.9),
            width=300,
            height=300,
        )
