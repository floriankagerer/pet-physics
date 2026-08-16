"""Data model for the MJCF `mesh` asset element.

Defines the `Mesh` dataclass, which mirrors the attributes of the `<mesh>` element in the MJCF XML schema and can be
serialized back to XML via `BaseMJCFObject.to_xml_string()`.
"""

from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


@dataclass
class Mesh(BaseMJCFObject):
    """Represents a mesh in a MuJoCo model.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset-mesh

    Attributes:
        name: The name of the mesh, used for referencing from a geom. If omitted, the mesh name equals the file name
            without the path and extension.
        file: The path to the file (STL, MSH or OBJ) from which the mesh vertex data is loaded.
        scale: The per-axis scaling applied to the vertex data. Negative values flip the mesh along the
            corresponding axis.
    """

    name: str
    file: str
    scale: tuple[float, float, float]
