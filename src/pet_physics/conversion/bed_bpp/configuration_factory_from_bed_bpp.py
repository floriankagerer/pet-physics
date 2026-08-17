"""Convert bed-bpp packing plans into MuJoCo model configurations.

Parse raw bed-bpp packing plan files into `PackingPlan` instances (for example using a project-specific parser), then
use `create_model_configuration_from_packing_plan` to convert a single `PackingPlan` into a `ModelConfiguration` or
`create_collection_model_configurations_from_packing_plans` to convert a list of `PackingPlan` objects into a
`CollectionModelConfiguration`.
"""

from __future__ import annotations

import structlog

from pet_physics.coloring import RGBA_BASE_COLORS
from pet_physics.conversion.bed_bpp.bed_bpp_to_mjcf import action_to_body_and_teleport, packing_plan_to_carrier_body
from pet_physics.data_model.evaluation.stability_check import StabilityCheck
from pet_physics.data_model.model_configuration import ModelConfiguration
from pet_physics.data_model.modeling.bodies_configuration import BodiesConfiguration
from pet_physics.data_model.modeling.collection_model_configuration import CollectionModelConfiguration
from pet_physics.data_model.packing.item import Item
from pet_physics.data_model.packing.packing_plan import PackingPlan

logger = structlog.get_logger(__name__)

_DEFAULT_ITEM_COLOR = "0.9 0.9 0.9 1.0"
"""The RGBA color used for an item when `body_special_coloring` is given but has no entry for its color key."""


def _get_color(color_mapper: dict[str, str], item: Item, body_special_coloring: dict[str, str] | None = None) -> str:
    """Returns the RGBA color string used for the given item.

    Args:
        color_mapper: A mutable mapping of color keys to RGBA color strings, updated in place when new colors
            are assigned.
        item: The item for which the color is returned.
        body_special_coloring: A mapping of color key to a custom RGBA color string.

    Returns:
        The RGBA color string used for the given item.
    """
    color_key = item.color_identifier

    if body_special_coloring is None:
        if color_key not in color_mapper:
            n_colors = len(color_mapper)
            color_mapper[color_key] = RGBA_BASE_COLORS[n_colors % len(RGBA_BASE_COLORS)]

        return color_mapper.get(color_key)

    if color_key in body_special_coloring:
        return body_special_coloring.get(color_key)

    return _DEFAULT_ITEM_COLOR


def create_bodies_configuration_from_packing_plan(
    packing_plan: PackingPlan,
    stability_check: StabilityCheck,
    body_special_coloring: dict[str, str] | None = None,
) -> BodiesConfiguration:
    """Assigns colors and assembles body and teleport data for every action in a bed-bpp packing plan.

    Args:
        packing_plan: The packing plan whose actions, i.e., item placements, are converted.
        stability_check: The required stability check, which influences the model creation.
        body_special_coloring: A mapping of color key to a custom RGBA color string.

    Returns:
        The bodies configuration for the placements of the packing plan's items.
    """
    bodies = []
    teleports = []
    color_mapper: dict[str, str] = {}

    for action in packing_plan.actions:
        color = _get_color(color_mapper, action.item, body_special_coloring)
        body, teleport = action_to_body_and_teleport(action, action.item.sequence, color, stability_check)
        bodies.append(body)
        teleports.append(teleport)

    return BodiesConfiguration(bodies, teleports)


def create_model_configuration_from_packing_plan(
    packing_plan: PackingPlan,
    stability_check: StabilityCheck,
    body_special_coloring: dict[str, str] | None = None,
    model_bin_as_freejoint_body: bool = False,
) -> ModelConfiguration:
    """Builds the carrier body and item body data for a MuJoCo simulation of a bed-bpp packing plan.

    Args:
        packing_plan: The bed-bpp packing plan to convert.
        stability_check: The required stability check, which influences the model creation.
        body_special_coloring: A mapping of color key to a custom RGBA color string.
        model_bin_as_freejoint_body: Whether the carrier body should have a freejoint. The carrier represents the
            surface the items are placed on, e.g., a bed or shelf.

    Returns:
        The model configuration for the given packing plan.
    """
    bodies_config = create_bodies_configuration_from_packing_plan(packing_plan, stability_check, body_special_coloring)
    carrier = packing_plan_to_carrier_body(packing_plan, as_freejoint_body=model_bin_as_freejoint_body)

    return ModelConfiguration(packing_plan.id, carrier, bodies_config.bodies, bodies_config.teleports)


def create_collection_model_configurations_from_packing_plans(
    packing_plans: list[PackingPlan],
    stability_check: StabilityCheck,
    body_special_coloring: dict[str, str] | None = None,
    model_bin_as_freejoint_body: bool = False,
) -> CollectionModelConfiguration:
    """Assembles a model configuration collection from a list of packing plans.

    Args:
        packing_plans: The packing plans to convert.
        stability_check: The required stability check, which influences the model creation.
        body_special_coloring: A mapping of color key to a custom RGBA color string.
        model_bin_as_freejoint_body: Whether each carrier body should have a freejoint. The carrier represents the
            surface the items are placed on, e.g., a pallet or rollcontainer.

    Returns:
        A `CollectionModelConfiguration` containing the model configurations for all provided packing plans.
    """
    model_configurations = CollectionModelConfiguration()

    for packing_plan in packing_plans:
        model_configuration = create_model_configuration_from_packing_plan(
            packing_plan=packing_plan,
            stability_check=stability_check,
            body_special_coloring=body_special_coloring,
            model_bin_as_freejoint_body=model_bin_as_freejoint_body,
        )
        model_configurations.add_config(model_configuration)

    return model_configurations
