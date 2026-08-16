"""Contains a class that represents a geometric shape."""

from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict

from dataclasses_json import dataclass_json

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


class GeomKwargs(TypedDict):
    """This class contains the kwargs for instantiating a `Geom` object."""

    name: str
    type: Literal["box", "cylinder", "mesh", "plane"]
    size: tuple[float, float, float]
    mass: float
    rgba: NotRequired[str]
    pos: NotRequired[tuple[float, float, float]]
    solimp: NotRequired[tuple[float, float, float]]
    solref: NotRequired[tuple[float, float]]
    mesh: NotRequired[str]
    material: NotRequired[str]
    friction: NotRequired[tuple[float, float, float]]
    gap: NotRequired[float]
    contype: NotRequired[int]
    conaffinity: NotRequired[int]


@dataclass_json
@dataclass
class Geom(BaseMJCFObject):
    """Class to represent a geometric shape.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-geom
    """

    name: str
    type: Literal["box", "cylinder", "mesh", "plane"]
    size: tuple[float, float, float]
    mass: float
    rgba: str | None = None
    pos: tuple[float, float, float] | None = None
    solimp: tuple[float, float, float] = (0.99, 0.99, 0.01)
    solref: tuple[float, float] = (0.02, 1)  # (0.01, 1)  # (0.001, 1)
    mesh: str | None = None
    material: str | None = None
    friction: tuple[float, float, float] | None = (1.0, 0.005, 0.0001)
    gap: float | None = 0.0
    contype: int | None = None
    conaffinity: int | None = None
