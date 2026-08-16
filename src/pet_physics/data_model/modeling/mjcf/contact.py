from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict

from dataclasses_json import dataclass_json

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


class ContactKwargs(TypedDict):
    """This class contains the kwargs for instantiating a `Contact` object."""

    internal: NotRequired[Literal["false"]]
    selfcollide: NotRequired[Literal["none"]]
    solref: NotRequired[tuple[float, float]]
    solimp: NotRequired[tuple[float, float, float]]
    friction: NotRequired[tuple[float, float, float]]


@dataclass_json
@dataclass
class Contact(BaseMJCFObject):
    """This class models the contacts of a `<flexcomp>` object.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-contact
    """

    internal: Literal["false"] = "false"
    selfcollide: Literal["none"] = "none"
    solref: tuple[float, float] = (0.01, 1.0)
    solimp: tuple[float, float, float] = (0.99, 0.99, 0.01)
    friction: tuple[float, float, float] = (0.5, 0.005, 0.0001)
