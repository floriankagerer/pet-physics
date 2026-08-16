"""This module tests the functions that convert rigid to soft."""

import numpy as np
import pytest

from pet_physics.data_model.modeling.mjcf.body import Body
from pet_physics.data_model.modeling.mjcf.contact import Contact, ContactKwargs
from pet_physics.data_model.modeling.mjcf.edge import Edge, EdgeKwargs
from pet_physics.data_model.modeling.mjcf.geom import Geom
from pet_physics.modeling.model_generation.rigid_to_soft import (
    convert_body_from_rigid_to_soft,
    get_soft_body_spacing_wrt_count,
)
from pet_physics.type_alias_definition import Position3d, Size3d


def _make_rigid_body(name: str = "box", pos: Position3d = (0.0, 0.0, 0.4), size: Size3d = (0.3, 0.2, 0.1)) -> Body:
    """Creates a rigid body with a single `Geom` child for testing purposes."""
    body = Body(name=name, pos=pos)
    geom = Geom(
        name=f"{name}.geom",
        type="box",
        size=size,
        mass=1.0,
        rgba=(1, 1, 0, 1),
    )
    body.add_child(geom)
    return body


def test_get_soft_body_spacing_wrt_count() -> None:
    """Tests whether the spacing for soft body objects is correctly calculated."""
    rigid_body_size = (0.3, 0.2, 0.1)
    count = (3, 3, 3)
    expected_soft_body_spacing = (0.3, 0.2, 0.1)

    actual_soft_body_spacing = get_soft_body_spacing_wrt_count(rigid_body_size=rigid_body_size, count=count)
    assert np.isclose(actual_soft_body_spacing, expected_soft_body_spacing).all()

    rigid_body_size = (0.3, 0.2, 0.1)
    count = (4, 3, 2)
    expected_soft_body_spacing = (0.2, 0.2, 0.2)

    actual_soft_body_spacing = get_soft_body_spacing_wrt_count(rigid_body_size=rigid_body_size, count=count)
    assert np.isclose(actual_soft_body_spacing, expected_soft_body_spacing).all()

    rigid_body_size = (0.3, 0.2, 0.1)
    count = (3, 2, 1)

    with pytest.raises(ValueError):
        _ = get_soft_body_spacing_wrt_count(rigid_body_size=rigid_body_size, count=count)


def test_convert_body_from_rigid_to_soft_uses_default_kwargs() -> None:
    """Tests whether the conversion produces the expected `Flexcomp` when using default kwargs."""
    rigid_body = _make_rigid_body(name="box", pos=(0.0, 0.0, 0.4), size=(0.3, 0.2, 0.1))
    count = (3, 3, 3)

    soft_body = convert_body_from_rigid_to_soft(rigid_body, count=count)

    assert soft_body.name == rigid_body.name
    assert soft_body.pos == rigid_body.pos
    assert soft_body.mass == rigid_body.geom.mass
    assert soft_body.rgba == rigid_body.geom.rgba
    assert soft_body.dim == 3
    assert soft_body.type == "grid"
    assert soft_body.count == count
    assert soft_body.radius == pytest.approx(0.000001)

    expected_spacing = get_soft_body_spacing_wrt_count(rigid_body.geom.size, count)
    assert np.isclose(soft_body.spacing, expected_spacing).all()


def test_convert_body_from_rigid_to_soft_adds_default_edge_and_contact_children() -> None:
    """Tests whether the default `Edge` and `Contact` children are added when no kwargs are given."""
    rigid_body = _make_rigid_body()

    soft_body = convert_body_from_rigid_to_soft(rigid_body)

    edges = [child for child in soft_body._children if isinstance(child, Edge)]
    contacts = [child for child in soft_body._children if isinstance(child, Contact)]
    assert len(edges) == 1
    assert len(contacts) == 1
    assert edges[0].equality == "true"
    assert contacts[0].internal == "false"
    assert contacts[0].selfcollide == "none"


def test_convert_body_from_rigid_to_soft_uses_given_edge_and_contact_kwargs() -> None:
    """Tests whether custom `edge_kwargs` and `contact_kwargs` are forwarded to the created children."""
    rigid_body = _make_rigid_body()
    edge_kwargs: EdgeKwargs = EdgeKwargs(equality="true")
    contact_kwargs: ContactKwargs = ContactKwargs(internal="false", selfcollide="none", friction=(0.2, 0.001, 0.0001))

    soft_body = convert_body_from_rigid_to_soft(rigid_body, edge_kwargs=edge_kwargs, contact_kwargs=contact_kwargs)

    contacts = [child for child in soft_body._children if isinstance(child, Contact)]
    assert len(contacts) == 1
    assert contacts[0].friction == (0.2, 0.001, 0.0001)


def test_convert_body_from_rigid_to_soft_default_count() -> None:
    """Tests whether the default `count` of (3, 3, 3) is used when not specified."""
    rigid_body = _make_rigid_body(size=(0.3, 0.2, 0.1))

    soft_body = convert_body_from_rigid_to_soft(rigid_body)

    assert soft_body.count == (3, 3, 3)
