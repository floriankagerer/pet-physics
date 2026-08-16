from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


@dataclass
class Worldbody(BaseMJCFObject):
    """Represents the worldbody in a MuJoCo model.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#world-body-r
    """

    pass
