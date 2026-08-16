"""Data model for the configuration of a template MuJoCo model."""

from dataclasses import dataclass

from pet_physics.data_model.modeling.mjcf.option import OptionKwargs


@dataclass
class TemplateModelConfig:
    """The configuration that is filled in a template of a MuJoCo model.

    Attributes:
        name: The name of the model.
        option_kwargs: Defines the parameters of the `<option ... />` section in a MuJoCo model.
    """

    name: str
    option_kwargs: OptionKwargs | None = None
