"""Tests for the body teleporter."""

from __future__ import annotations

import mujoco
import numpy as np
import pytest

from pet_physics.data_model.evaluation.stability_check import StabilityCheck, StabilityCheckConfiguration
from pet_physics.data_model.teleport import Teleport
from pet_physics.simulation.body_teleporter import SIDEWAYS_OVERLAP_TOLERANCE_M, BodyTeleporter

HALF_SIZE = 0.05
PARKING_POSITION = (2.0, 2.0, HALF_SIZE)


@pytest.fixture
def model() -> mujoco.MjModel:
    """Two placed boxes with a gap between them and one box that waits to be teleported."""
    xml = f"""
    <mujoco model="body_teleporter_test_model">
      <worldbody>
        <geom name="ground" type="plane" size="5 5 0.1" />
        <body name="box_left" pos="0 0 {HALF_SIZE}">
          <freejoint />
          <geom type="box" size="{HALF_SIZE} {HALF_SIZE} {HALF_SIZE}" mass="1" />
        </body>
        <body name="box_right" pos="0.3 0 {HALF_SIZE}">
          <freejoint />
          <geom type="box" size="{HALF_SIZE} {HALF_SIZE} {HALF_SIZE}" mass="1" />
        </body>
        <body name="box_new" pos="{PARKING_POSITION[0]} {PARKING_POSITION[1]} {PARKING_POSITION[2]}">
          <freejoint />
          <geom type="box" size="{HALF_SIZE} {HALF_SIZE} {HALF_SIZE}" mass="1" />
        </body>
      </worldbody>
    </mujoco>
    """
    return mujoco.MjModel.from_xml_string(xml)


def _teleport_box_new(model: mujoco.MjModel, target_position: tuple[float, float, float]) -> np.ndarray:
    """Teleports `box_new` to the target position and returns the position it ends up at."""
    stability_check = StabilityCheck(
        check_type="one_by_one", check_configuration=StabilityCheckConfiguration(parameters={})
    )
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)

    teleporter = BodyTeleporter(model, stability_check)
    teleporter.set_teleports([Teleport("box_new", target_position, PARKING_POSITION)], simulation_time=0.0)
    teleporter.apply_next_teleport(data, simulation_time=0.0)

    mujoco.mj_forward(model, data)
    return data.body("box_new").xpos.copy()


def test_teleport_without_overlap_places_body_at_target(model: mujoco.MjModel) -> None:
    target_position = (0.15, 0.0, HALF_SIZE)

    position = _teleport_box_new(model, target_position)

    np.testing.assert_allclose(position, target_position, atol=1e-9)


def test_teleport_into_neighbour_moves_body_out_sideways(model: mujoco.MjModel) -> None:
    overlap = 0.003
    target_position = (2 * HALF_SIZE - overlap, 0.0, HALF_SIZE)

    position = _teleport_box_new(model, target_position)

    assert position[0] == pytest.approx(2 * HALF_SIZE, abs=2 * SIDEWAYS_OVERLAP_TOLERANCE_M)
    assert position[1] == pytest.approx(0.0, abs=1e-9)
    assert position[2] == pytest.approx(HALF_SIZE, abs=1e-9)


def test_teleport_onto_neighbour_keeps_body_at_target(model: mujoco.MjModel) -> None:
    target_position = (0.02, 0.0, 3 * HALF_SIZE - 0.003)

    position = _teleport_box_new(model, target_position)

    np.testing.assert_allclose(position, target_position, atol=1e-9)
