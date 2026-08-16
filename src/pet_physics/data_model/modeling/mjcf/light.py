"""Data model for the MJCF `light` body element.

Defines the `Light` dataclass, which mirrors a subset of the attributes of the `<light>` element in the MJCF XML schema
and can be serialized back to XML via `BaseMJCFObject.to_xml_string()`.
"""

from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject
from pet_physics.type_alias_definition import Position3d


@dataclass
class Light(BaseMJCFObject):
    """Represents a light in a MuJoCo model.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light

    Attributes:
        diffuse: The diffuse color of the light under the default Phong lighting model.
        pos: The position of the light. This only affects rendering for spotlights, but should also be set for
            directional lights since it is used to render the light's decorative object.
        dir: The direction in which the light shines.
    """

    diffuse: tuple[float, float, float]
    pos: Position3d
    dir: tuple[float, float, float]
