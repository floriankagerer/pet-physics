"""Tests for the acceleration recorder."""

from __future__ import annotations

import mujoco
import numpy as np

from pet_physics.simulation.physical_quantities.quantity_names import QuantityName
from pet_physics.simulation.physical_quantities.recorders.acceleration_recorder import AccelerationRecorder

BODY_NAMES = ["box_a", "box_b", "box_c"]


def _model() -> mujoco.MjModel:
    """Three boxes with a free joint each."""
    bodies = "".join(
        f"""
        <body name="{body_name}" pos="{index} 0 0.05">
          <freejoint />
          <geom type="box" size="0.05 0.05 0.05" mass="1" />
        </body>"""
        for index, body_name in enumerate(BODY_NAMES)
    )
    return mujoco.MjModel.from_xml_string(f"<mujoco><worldbody>{bodies}</worldbody></mujoco>")


def test_record_assigns_each_body_its_own_acceleration() -> None:
    model = _model()
    data = mujoco.MjData(model)
    data.qacc[:] = np.arange(model.nv)

    recorder = AccelerationRecorder(mj_model=model, bodies=BODY_NAMES, n_steps=1)
    recorder.record(step_index=0, model=model, data=data)

    ((quantity_name, history),) = recorder.get_quantity_history_registrations()
    assert quantity_name == QuantityName.ACCELERATION
    for body_index, body_name in enumerate(BODY_NAMES):
        acceleration = history.get_values_of_body(body_name)[0]
        np.testing.assert_array_equal(acceleration.linear_acceleration, 6 * body_index + np.arange(3))
        np.testing.assert_array_equal(acceleration.angular_acceleration, 6 * body_index + 3 + np.arange(3))
