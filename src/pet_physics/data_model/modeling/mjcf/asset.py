"""Data class that represents the asset part."""

from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


@dataclass
class Asset(BaseMJCFObject):
    """Represents the asset part in a MuJoCo model.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#asset
    """

    pass
