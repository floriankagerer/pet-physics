from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.mesh import Mesh
from pet_physics.modeling import PATH_PLACEHOLDER


@dataclass
class MeshCone(Mesh):
    """Class to represent the mesh for a cone in a MuJoCo model. This object belongs to the `asset` part of a model."""

    def __init__(self) -> None:
        super().__init__(
            name="mesh.cone",
            file=f"{PATH_PLACEHOLDER}/mjcf_template/asset/mesh_cone.obj",
            scale=(0.05, 0.05, 0.05),
        )
