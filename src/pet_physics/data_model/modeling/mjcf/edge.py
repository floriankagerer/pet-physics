from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict

from dataclasses_json import dataclass_json

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


class EdgeKwargs(TypedDict):
    """This class contains the kwargs for instantiating an `Edge` object."""

    equality: NotRequired[Literal["true"]]


@dataclass_json
@dataclass
class Edge(BaseMJCFObject):
    """This class is used to represent the properties of all edges in a `<flexcomp>` object.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#flexcomp-edge
    """

    equality: Literal["true"] = "true"
