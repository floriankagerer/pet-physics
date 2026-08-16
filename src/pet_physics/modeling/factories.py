"""Factory functions for creating MuJoCo model data model instances."""

from typing import Literal, TypeAlias

from pet_physics.data_model.modeling.mjcf.body import Body, BodyKwargs
from pet_physics.data_model.modeling.mjcf.body_freejoint import BodyFreejoint
from pet_physics.data_model.modeling.mjcf.contact import Contact, ContactKwargs
from pet_physics.data_model.modeling.mjcf.edge import Edge, EdgeKwargs
from pet_physics.data_model.modeling.mjcf.flexcomp import Flexcomp, FlexcompKwargs
from pet_physics.data_model.modeling.mjcf.geom import Geom, GeomKwargs
from pet_physics.data_model.modeling.mjcf.mujoco_model import MuJoCoModel
from pet_physics.data_model.modeling.template_model_config import TemplateModelConfig
from pet_physics.modeling.model_templates.palletizing_template_model import (
    PalletizingTemplateModel,
)
from pet_physics.modeling.named_objects.cardboard import CARDBOARD_FRICTION, CardboardGeom

ModelFromTemplate: TypeAlias = PalletizingTemplateModel


def _add_bodies_to_model(model: ModelFromTemplate, bodies: list[Body]) -> MuJoCoModel:
    """Adds bodies to the worldbody section of the MuJoCo model.

    Args:
        model: The template of a MuJoCo model.
        bodies: The bodies to add to the model's worldbody.

    Returns:
        The model with the added bodies.
    """
    for body in bodies:
        model.worldbody.add_child(body)

    return model


def make_palletizing_model(
    template: Literal["palletizing"],
    template_config: TemplateModelConfig,
    carrier: Body,
    boxes: list[Body],
) -> MuJoCoModel:
    """Creates a MuJoCo model from the selected template with carrier and boxes added.

    Args:
        template: The model template to use.
        template_config: The configuration of the template.
        carrier: The carrier body of the palletization.
        boxes: The boxes to place on the carrier.

    Returns:
        The assembled MuJoCo model.

    Raises:
        NotImplementedError: If the specified template is not available.
    """
    if template == "palletizing":
        model = PalletizingTemplateModel.from_config(template_config)
    else:
        raise NotImplementedError(f"template '{template}' is not available")

    return _add_bodies_to_model(model, [carrier] + boxes)


def make_freejoint_body(
    material: Literal["cardboard"], geom_kwargs: GeomKwargs, body_kwargs: BodyKwargs
) -> BodyFreejoint:
    """Creates a freejoint body using the specified material and geometry settings.

    Args:
        material: The material type, which determines the geom class used to construct the body.
        geom_kwargs: Keyword arguments for the geom constructor.
        body_kwargs: Keyword arguments for the `BodyFreejoint` constructor.

    Returns:
        The constructed freejoint body.
    """
    if material == "cardboard":
        geom_class = CardboardGeom
    else:
        geom_class = Geom

    geom = geom_class(**geom_kwargs)

    body = BodyFreejoint(**body_kwargs)
    body.add_child(geom)

    return body


def make_soft_body(
    material: Literal["cardboard"],
    flexcomp_kwargs: FlexcompKwargs,
    edge_kwargs: EdgeKwargs,
    contact_kwargs: ContactKwargs,
) -> Flexcomp:
    """Creates a soft body with the specified material and component settings.

    Args:
        material: The material type, which determines the friction value applied to the body's contact element.
        flexcomp_kwargs: Keyword arguments for the `Flexcomp` constructor.
        edge_kwargs: Keyword arguments for the `Edge` constructor.
        contact_kwargs: Keyword arguments for the `Contact` constructor.

    Returns:
        The constructed soft body.
    """

    soft_body = Flexcomp(**flexcomp_kwargs)

    edge = Edge(**edge_kwargs)
    contact = Contact(**contact_kwargs)
    if material == "cardboard":
        contact.friction = CARDBOARD_FRICTION

    soft_body.add_child(edge).add_child(contact)

    return soft_body
