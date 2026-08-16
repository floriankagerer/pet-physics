"""Module that contains a class that represent a free joint."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


@dataclass_json
@dataclass
class Freejoint(BaseMJCFObject):
    """Class to represent a freejoint object in MuJoCo.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-freejoint
    """

    pass
