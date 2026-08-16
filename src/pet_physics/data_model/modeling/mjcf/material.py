"""Data model for the MJCF `material` asset element.

Defines the `Material` dataclass, which mirrors a subset of the attributes of the `<material>` element in the MJCF XML
schema and can be serialized back to XML via `BaseMJCFObject.to_xml_string()`.
"""

from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


@dataclass
class Material(BaseMJCFObject):
    """Represents a material in a MuJoCo model.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-material

    Attributes:
        name: The name of the material, used for referencing from a geom, site, or tendon.
        rgba: The color and transparency of the material. Texture colors, if assigned, are multiplied component-wise
            with this value.
        texture: The name of the texture asset applied to the material.
        texrepeat: The number of times a 2D texture image is repeated over the object, relative to the object size or
            a spatial unit.
        texuniform: Whether cube mapping is applied to a unit object before scaling ("true"), or directly using the
            object's actual size ("false").
        reflectance: The strength of the simulated reflectance, applied only when the material is used on a plane or
            box geom.
    """

    name: str
    rgba: tuple[float, float, float, float] | None = None
    texture: str | None = None
    texrepeat: str | None = None
    texuniform: str | None = None
    reflectance: float | None = None
