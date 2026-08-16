"""This module generates MuJoCo models based on model generation configurations."""

from collections.abc import Callable

import structlog

from pet_physics.data_model.model_configuration import ModelConfiguration
from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.modeling.mjcf.flexcomp import Flexcomp
from pet_physics.data_model.modeling.mjcf.mujoco_model import MuJoCoModel
from pet_physics.data_model.modeling.template_model_config import TemplateModelConfig
from pet_physics.modeling.factories import make_palletizing_model
from pet_physics.modeling.model_generation.model_generator_configuration import ModelGeneratorConfiguration

logger = structlog.get_logger(__name__)


class ModelGenerator:
    """The model generator creates MuJoCo models for a given `ModelConfiguration` instance and a
    certain `ModelGeneratorConfiguration`.

    This can be helpful if you want to simulate the same packing, but with different configurations. As an example,
    with this generator you are able to create two different MuJoCo models for the same packing, one that models the
    boxes as rigid bodies, the other models the boxes as soft bodies.
    """

    @staticmethod
    def apply_box_converter_to_boxes(
        box_converter: Callable[[Body | Flexcomp], Body | Flexcomp], boxes: list[Body | Flexcomp]
    ) -> list[Body | Flexcomp]:
        """Applies the given box converter method to the given boxes.

        For example, this method can be used to convert rigid body objects to soft body objects.

        Args:
            box_converter: The function that converts a box from one type to another (e.g., rigid to soft).
            boxes: The boxes to that the box converter method is applied.

        Returns:
            The boxes after applying the box converter method.
        """
        return [box_converter(box) for box in boxes]

    @staticmethod
    def generate(
        generator_configuration: ModelGeneratorConfiguration, model_configuration: ModelConfiguration
    ) -> MuJoCoModel:
        """Generates a MuJoCo model based on both, the model configuration and the generator configuration.

        Args:
            generator_configuration: Defines which options are used an whether the boxes given in the
                model configuration needs to be converted wrt. the configuration.
            model_configuration: The model configuration for a single bin. It contains the name of the model,
                the carrier, the boxes, and the teleports.

        Returns:
            The generated simulation model with the proper options.
        """
        logger.info(f"generate model for configuration '{generator_configuration.configuration_name}'")
        carrier = model_configuration.carrier
        boxes = ModelGenerator.apply_box_converter_to_boxes(
            generator_configuration.box_converter, model_configuration.boxes
        )

        template_config = TemplateModelConfig(model_configuration.model_name, generator_configuration.option_kwargs)
        model = make_palletizing_model("palletizing", template_config, carrier, boxes)
        logger.info("completed generation of model")
        return model
