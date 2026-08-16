"""This module contains functions to convert rigid body objects to soft body objects."""

from typing import Optional

from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.modeling.mjcf.contact import Contact, ContactKwargs
from pet_physics.data_model.modeling.mjcf.edge import Edge, EdgeKwargs
from pet_physics.data_model.modeling.mjcf.flexcomp import Flexcomp
from pet_physics.type_alias_definition import Size3d, Vector3d


def get_soft_body_spacing_wrt_count(rigid_body_size: Size3d, count: tuple[int, int, int]) -> Vector3d:
    """Calculates the point spacing of a soft body given the rigid body size and point count.

    Args:
        rigid_body_size: The size of the rigid body, i.e., half of the size of the real world body. In other words,
            the actual size of a box is twice the value of `rigid_body_size`.
        count: The number of automatically generated points in each dimension.

    Returns:
        The spacing between the generated points in each dimension.
    """
    if min(count) < 2:
        raise ValueError("any value of count must not be smaller than 2")

    soft_body_spacing = []
    for i_count, i_half_size in zip(count, rigid_body_size):
        actual_body_size = i_half_size * 2
        parts = i_count - 1
        i_spacing = actual_body_size / parts

        soft_body_spacing.append(i_spacing)

    return tuple(soft_body_spacing)


def convert_body_from_rigid_to_soft(
    rigid_body: Body,
    count: tuple[int, int, int] = (3, 3, 3),
    edge_kwargs: Optional[EdgeKwargs] = None,
    contact_kwargs: Optional[ContactKwargs] = None,
) -> Flexcomp:
    """Converts a rigid `Body` object to an equivalent soft `Flexcomp` object.

    Args:
        rigid_body: The rigid body to convert.
        count: The number of automatically generated points in each dimension. edge_kwargs: Keyword arguments for
            the edge element.
        contact_kwargs: Keyword arguments for the contact element.

    Returns:
        The soft body equivalent of the rigid body.
    """
    if edge_kwargs is None:
        edge_kwargs = EdgeKwargs(equality="true")
    if contact_kwargs is None:
        contact_kwargs = ContactKwargs(internal="false", selfcollide="none")

    edge = Edge(**edge_kwargs)
    contact = Contact(**contact_kwargs)

    soft_body_spacing = get_soft_body_spacing_wrt_count(rigid_body.geom.size, count)

    soft_body = Flexcomp(
        name=rigid_body.name,
        pos=rigid_body.pos,
        mass=rigid_body.geom.mass,
        spacing=soft_body_spacing,
        dim=3,
        type="grid",
        count=count,
        rgba=rigid_body.geom.rgba,
        radius=0.000001,
    )

    soft_body.add_child(edge).add_child(contact)
    return soft_body
