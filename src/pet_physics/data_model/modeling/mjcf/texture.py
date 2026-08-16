"""Data model for the MJCF `texture` asset element.

Defines the `Texture` dataclass, which mirrors the attributes of the
`<texture>` element in the MJCF XML schema and can be serialized back to XML
via `BaseMJCFObject.to_xml_string()`.
"""

from dataclasses import dataclass
from typing import Literal

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


@dataclass
class Texture(BaseMJCFObject):
    """Represents a texture in a MuJoCo model.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-texture

    Attributes:
        name: The name of the texture, used for referencing from a material.
        type: Whether the texture is mapped as a 2D image or as a skybox.
        builtin: The procedural pattern used to generate the texture.
        width: The width of the procedural texture, in pixels.
        height: The height of the procedural texture, in pixels.
        rgb1: The first color used for procedural texture generation.
        rgb2: The second color used for procedural texture generation.
        mark: The style of markings drawn on top of the procedural texture.
        markrgb: The color used for the procedural texture markings.
    """

    name: str
    type: Literal["2d", "skybox"]
    builtin: Literal["checker", "flat"]
    width: int
    height: int
    rgb1: tuple[float, float, float]
    rgb2: tuple[float, float, float] | None = None
    mark: Literal["edge"] | None = None
    markrgb: tuple[float, float, float] | None = None
