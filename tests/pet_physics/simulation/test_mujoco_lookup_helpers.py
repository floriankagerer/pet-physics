"""Tests for MuJoCo lookup helper utilities."""

from __future__ import annotations

import mujoco
import numpy as np
import pytest

from pet_physics.simulation.mujoco_lookup_helpers import (
    get_body_contacts,
    get_body_id,
    get_body_names_in_model,
    get_contacts_of_geometry,
    get_geom_names_of_body,
    get_joint_start_address_of_body,
    get_position_of_body,
    id_of_geom_name,
    name_of_geom_id,
)


@pytest.fixture
def model() -> mujoco.MjModel:
    """A minimal MuJoCo model for lookup and contact tests."""
    xml = """
    <mujoco model="lookup_helpers_test_model">
      <worldbody>
        <geom name="ground" type="plane" size="1 1 0.1" />
        <body name="_private_body" pos="0.5 0 0.2">
          <freejoint />
          <geom name="private_geom" type="box" size="0.05 0.05 0.05" mass="1" />
        </body>
        <body name="box_a" pos="0 0 0.05">
          <freejoint />
          <geom name="box_a_geom" type="box" size="0.05 0.05 0.05" mass="1" />
        </body>
        <body name="box_b" pos="0.3 0 0.05">
          <freejoint />
          <geom name="box_b_geom" type="box" size="0.05 0.05 0.05" mass="1" />
        </body>
      </worldbody>
    </mujoco>
    """
    return mujoco.MjModel.from_xml_string(xml)


@pytest.fixture
def data(model: mujoco.MjModel) -> mujoco.MjData:
    """Simulation data with up-to-date contacts for the fixture model."""
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    return data


def _contacts(data: mujoco.MjData) -> list[mujoco.MjContact]:
    """Return active contacts from MuJoCo data."""
    return [data.contact[c_idx] for c_idx in range(data.ncon)]


def test_geom_name_and_id_lookup_roundtrip(model: mujoco.MjModel) -> None:
    """Geom id and name lookup should be inverse operations for existing geoms."""
    geom_id = id_of_geom_name(model, "box_a_geom")
    assert geom_id >= 0
    assert name_of_geom_id(model, geom_id) == "box_a_geom"


def test_get_contacts_of_geometry_returns_all_contacts_when_geom_name_is_none(
    model: mujoco.MjModel, data: mujoco.MjData
) -> None:
    """When no geom is provided, all contacts should be returned with original indices."""
    all_contacts = _contacts(data)
    indexed_contacts = get_contacts_of_geometry(model, all_contacts, geom_name=None)

    assert [c_idx for c_idx, _ in indexed_contacts] == list(range(len(all_contacts)))
    assert len(indexed_contacts) == len(all_contacts)


def test_get_contacts_of_geometry_filters_contacts_for_geom(model: mujoco.MjModel, data: mujoco.MjData) -> None:
    """Filtering by geometry should keep only contacts containing that geometry."""
    all_contacts = _contacts(data)
    box_a_geom_id = id_of_geom_name(model, "box_a_geom")

    filtered_contacts = get_contacts_of_geometry(model, all_contacts, geom_name="box_a_geom")

    assert len(filtered_contacts) > 0
    assert all(c.geom1 == box_a_geom_id or c.geom2 == box_a_geom_id for _, c in filtered_contacts)


def test_get_contacts_of_geometry_returns_empty_list_for_missing_geom_name(
    model: mujoco.MjModel, data: mujoco.MjData
) -> None:
    """Filtering by a non-existing geometry name should yield no contacts."""
    filtered_contacts = get_contacts_of_geometry(model, _contacts(data), geom_name="missing_geom")
    assert filtered_contacts == []


def test_get_body_names_in_model_defaults_exclude_private_and_world(model: mujoco.MjModel) -> None:
    """Default body-name lookup excludes private names and world."""
    body_names = get_body_names_in_model(model)

    assert "world" not in body_names
    assert "_private_body" not in body_names
    assert "box_a" in body_names
    assert "box_b" in body_names


def test_get_body_names_in_model_can_include_private_and_world(model: mujoco.MjModel) -> None:
    """Body-name lookup includes world and private bodies when configured to do so."""
    body_names = get_body_names_in_model(
        model,
        ignore_private_bodies=False,
        ignore_additional_bodies=[],
    )

    assert "world" in body_names
    assert "_private_body" in body_names


def test_get_body_id_and_get_geom_names_of_body(model: mujoco.MjModel) -> None:
    """Body and geometry lookup helpers should resolve known names correctly."""
    box_a_body_id = get_body_id(model, "box_a")
    expected_body_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "box_a")

    assert box_a_body_id == expected_body_id
    assert get_geom_names_of_body(model, "box_a") == ["box_a_geom"]


def test_get_joint_start_address_of_body(model: mujoco.MjModel) -> None:
    """Joint start address should match MuJoCo model indexing for the body."""
    box_a_body_id = get_body_id(model, "box_a")
    expected_address = model.jnt_qposadr[model.body_jntadr[box_a_body_id]]

    assert get_joint_start_address_of_body(model, "box_a") == expected_address


def test_get_position_of_body(model: mujoco.MjModel) -> None:
    """Body position helper should return the model-defined body position."""
    position = get_position_of_body(model, "box_a")
    np.testing.assert_allclose(position, np.array([0.0, 0.0, 0.05]))


def test_get_body_contacts_contains_geom_names_and_on_top_member(model: mujoco.MjModel, data: mujoco.MjData) -> None:
    """Body contacts should contain geom names and a valid on-top geometry name."""
    body_contacts = get_body_contacts(model, data)

    assert len(body_contacts) > 0
    for geom1_name, geom2_name, geom_on_top in body_contacts:
        assert isinstance(geom1_name, str)
        assert isinstance(geom2_name, str)
        assert geom_on_top in {geom1_name, geom2_name}

    assert any({geom1_name, geom2_name} == {"ground", "box_a_geom"} for geom1_name, geom2_name, _ in body_contacts)
