"""Classes responsible for configuring the MuJoCo model generation behavior."""

import re
from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from pet_physics.data_model.modeling.mjcf.option import OptionKwargs
from pet_physics.modeling.model_generation.rigid_to_soft import convert_body_from_rigid_to_soft


def identity(x: Any) -> Any:
    """Returns the given object."""
    return x


@dataclass
class ModelGeneratorConfiguration(ABC):
    """The base class of a configuration for the `ModelGenerator`. This configuration is used to generate
    a MuJoCo model, based on a `ModelConfiguration` instance.

    Attributes:
        option_kwargs: Defines the parameters of the `<option ... />` section in a MuJoCo model.
        box_converter: This callable defines which function is applied to convert the boxes defined in a
            `ModelConfiguration` instance. By default, the `box_converter` is the identity.
    """

    option_kwargs: OptionKwargs = field(default_factory=OptionKwargs)
    box_converter: Callable = identity

    @property
    def configuration_name(self) -> str:
        """Returns the configuration name, i.e., the class name, as string in kebab case, e.g.,
        `FooBar -> "foo-bar"`."""
        kebab = re.sub(r"(?<!^)(?=[A-Z])", "-", self.__class__.__name__).lower()
        return kebab


@dataclass
class RigidNewton(ModelGeneratorConfiguration):
    """This configuration defines that the model generator uses

    - *Newton's method* as solver, cf. [MuJoCo - Algorithms: Newton](https://mujoco.readthedocs.io/en/stable/computation/index.html#soalgorithms),
    - and *rigid bodies* for the boxes.
    """

    def __init__(self):
        option_kwargs = OptionKwargs(solver="Newton")

        super().__init__(option_kwargs=option_kwargs, box_converter=identity)


@dataclass
class RigidCG(ModelGeneratorConfiguration):
    """This configuration defines that the model generator uses

    - *conjugate gradient method* as solver, cf. [MuJoCo - Algorithms: CG](https://mujoco.readthedocs.io/en/stable/computation/index.html#soalgorithms),
    - and *rigid bodies* for the boxes.
    """

    def __init__(self):
        option_kwargs = OptionKwargs(solver="CG")

        super().__init__(option_kwargs=option_kwargs, box_converter=identity)


@dataclass
class SoftNewton(ModelGeneratorConfiguration):
    """This configuration defines that the model generator uses

    - *Newton's method* as solver, cf. [MuJoCo - Algorithms: Newton](https://mujoco.readthedocs.io/en/stable/computation/index.html#soalgorithms),
    - and *soft bodies* for the boxes.
    """

    def __init__(self):
        option_kwargs = OptionKwargs(solver="Newton")

        super().__init__(option_kwargs=option_kwargs, box_converter=convert_body_from_rigid_to_soft)
