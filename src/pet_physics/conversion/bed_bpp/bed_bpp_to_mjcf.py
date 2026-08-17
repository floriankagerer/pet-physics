"""Utility functions for converting bed-bpp packing plan objects to MuJoCo model elements."""

import numpy as np

from pet_physics.data_model.evaluation.stability_check import StabilityCheck
from pet_physics.data_model.modeling.mjcf.body import Body, BodyKwargs
from pet_physics.data_model.modeling.mjcf.freejoint import Freejoint
from pet_physics.data_model.modeling.mjcf.geom import Geom, GeomKwargs
from pet_physics.data_model.packing.action import Action
from pet_physics.data_model.packing.orientation import Orientation
from pet_physics.data_model.packing.packing_plan import PackingPlan
from pet_physics.data_model.teleport import Teleport
from pet_physics.modeling.factories import make_freejoint_body
from pet_physics.utils.mjcf_utils import MJCFUtils, get_body_and_geom_name

_CARRIER_HALF_HEIGHT_M = 0.072
"""Half the thickness, in meters, of the flat carrier body representing a bed-bpp packing surface."""

_CARRIER_MASS_KG = 25.0
"""The mass, in kilograms, assigned to the carrier body."""

_CARRIER_RGBA = "0.871 0.722 0.529 1"
"""The RGBA color of the carrier body."""

_CARRIER_FRICTION = (3.0, 0.005, 0.0001)
"""The sliding, torsional, and rolling friction of the carrier body."""


def _compute_footprint_size_mm(packing_plan: PackingPlan) -> tuple[float, float]:
    """Computes the (length, width) footprint spanned by all items of a packing plan.

    The bed-bpp format does not define an explicit carrier size, so the footprint is derived as the bounding box
    spanned by all placed items.

    Args:
        packing_plan: The packing plan whose footprint is computed.

    Returns:
        The `(length_mm, width_mm)` footprint of the packing plan.

    Raises:
        ValueError: If the packing plan has no actions.
    """
    if not packing_plan.actions:
        raise ValueError(f"cannot compute a footprint for packing plan '{packing_plan.id}' with no actions")

    max_length_mm = 0.0
    max_width_mm = 0.0
    for action in packing_plan.actions:
        item_length_mm, item_width_mm, _ = Orientation(action.orientation).get_item_size(action.item)
        max_length_mm = max(max_length_mm, action.flb_coordinates.x + item_length_mm)
        max_width_mm = max(max_width_mm, action.flb_coordinates.y + item_width_mm)

    return max_length_mm, max_width_mm


def packing_plan_to_carrier_body(packing_plan: PackingPlan, as_freejoint_body: bool = False) -> Body:
    """Converts a bed-bpp `PackingPlan` to a MuJoCo carrier `Body`.

    Args:
        packing_plan: The packing plan whose bounding footprint defines the carrier.
        as_freejoint_body: Whether the body should have a freejoint.

    Returns:
        The carrier body representing the packing plan's surface.
    """
    body_name, geom_name = get_body_and_geom_name("", f"{packing_plan.id}-carrier")

    footprint_size_mm = (*_compute_footprint_size_mm(packing_plan), 0.0)
    converted_size, _ = MJCFUtils.convert_to_mjcf_coordinates(
        flb=(0, 0, 0), size=footprint_size_mm, size_reduction=0.0, unit="mm"
    )
    size_1, size_2 = converted_size[0], converted_size[1]

    geom = Geom(
        name=geom_name,
        type="box",
        size=(size_1, size_2, _CARRIER_HALF_HEIGHT_M),
        mass=_CARRIER_MASS_KG,
        rgba=_CARRIER_RGBA,
        friction=_CARRIER_FRICTION,
    )

    carrier = Body(name=body_name, pos=(size_1, size_2, -_CARRIER_HALF_HEIGHT_M))
    carrier.add_child(geom)

    if as_freejoint_body:
        carrier.add_child(Freejoint())

    return carrier


def action_to_body_and_teleport(
    action: Action, counter: int, color: str, stability_check: StabilityCheck
) -> tuple[Body, Teleport]:
    """Converts a bed-bpp `Action` to a MuJoCo `Body` and a `Teleport`.

    Args:
        action: The action, i.e., item placement, to convert.
        counter: A counter used to generate unique body names and, for the `"one_by_one"` stability check, the
            dummy initial position.
        color: The RGBA color string for this body.
        stability_check: The required stability check, which influences the initial body position.

    Returns:
        A tuple of the converted body and its teleport.

    Raises:
        NotImplementedError: If the stability check type is neither `"one_by_one"` nor `"static"`.
    """
    item = action.item
    oriented_size_mm = Orientation(action.orientation).get_item_size(item)
    box_size_reduction_mm = stability_check.check_configuration.box_size_reduction_absolute_mm
    size_tuple, flb_tuple = MJCFUtils.convert_to_mjcf_coordinates(
        flb=action.flb_coordinates.xyz, size=oriented_size_mm, size_reduction=box_size_reduction_mm, unit="mm"
    )

    body_name, geom_name = get_body_and_geom_name(counter, f"{item.article}_{item.id}_{item.sequence}")

    if stability_check.is_type_one_by_one:
        # use a dummy position as initial position
        dummy_position = counter * np.array([1.0, 1.0, 0]) + np.array([2.0, 2.0, size_tuple[2]])
        body_initial_position = tuple(dummy_position.tolist())

    elif stability_check.is_type_static:
        body_initial_position = flb_tuple

    else:
        msg = f"check type {stability_check.check_type} is not implemented"
        raise NotImplementedError(msg)

    teleport = Teleport(body_name, flb_tuple, body_initial_position)

    # always use a dummy position for the box position
    geom_kwargs = GeomKwargs(name=geom_name, type="box", size=size_tuple, mass=item.weight_kg, rgba=color)
    body_kwargs = BodyKwargs(name=body_name, pos=body_initial_position)
    body = make_freejoint_body("cardboard", geom_kwargs, body_kwargs)

    return body, teleport
