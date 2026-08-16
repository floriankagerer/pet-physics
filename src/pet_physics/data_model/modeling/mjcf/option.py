from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict

from pet_physics.data_model.modeling.mjcf.base_mjcf_object import BaseMJCFObject


class OptionKwargs(TypedDict):
    """This class contains the kwargs for instantiating an `Option` object.

    Attributes:
        timestep: The simulation time step in seconds.
        gravity: Defines the value of the gravity that is used. MuJoCo uses `"(0, 0, -9.81)` if not specified.
        integrator: Defines the numerical integrator to be used.
        cone: he type of contact friction cone. MuJoCo uses `"pyramidal` if not specified.
        solver: The type of constraint solver that is used. MuJoCo uses `"Newton"` if not specified.
    """

    timestep: NotRequired[float] = None
    gravity: NotRequired[tuple[float, float, float]] = None
    integrator: NotRequired[Literal["implicitfast"]] = None
    cone: NotRequired[Literal["elliptic", "pyramidal"]] = None
    solver: NotRequired[Literal["Newton", "CG"]] = None


@dataclass
class Option(BaseMJCFObject):
    """Represents the options in a MuJoCo model.

    For details, visit https://mujoco.readthedocs.io/en/stable/XMLreference.html#option

    Attributes:
        timestep: The simulation time step in seconds.
        gravity: Defines the value of the gravity that is used. MuJoCo uses `"(0, 0, -9.81)` if not specified.
        integrator: Defines the numerical integrator to be used.
        cone: he type of contact friction cone. MuJoCo uses `"pyramidal` if not specified.
        solver: The type of constraint solver that is used. MuJoCo uses `"Newton"` if not specified.
    """

    timestep: float | None = None
    gravity: tuple[float, float, float] | None = None
    integrator: Literal["implicitfast"] | None = None
    cone: Literal["elliptic", "pyramidal"] | None = None
    solver: Literal["Newton", "CG"] | None = None
