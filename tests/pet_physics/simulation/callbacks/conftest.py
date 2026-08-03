"""Shared fixtures for `simulation.callbacks` tests."""

from unittest.mock import MagicMock

import mujoco
import pytest

_MINIMAL_MODEL_XML = """
<mujoco model="callback_test_model">
  <worldbody>
    <geom name="ground" type="plane" size="1 1 0.1" />
    <body name="box_a" pos="0 0 0.5">
      <freejoint />
      <geom name="box_a_geom" type="box" size="0.1 0.1 0.1" mass="1" />
    </body>
    <body name="box_b" pos="0.5 0 0.5">
      <freejoint />
      <geom name="box_b_geom" type="box" size="0.1 0.1 0.1" mass="1" />
    </body>
  </worldbody>
</mujoco>
"""


@pytest.fixture
def mj_model() -> mujoco.MjModel:
    """A minimal MuJoCo model with two named free bodies for callback tests."""
    return mujoco.MjModel.from_xml_string(_MINIMAL_MODEL_XML)


@pytest.fixture
def mj_data(mj_model: mujoco.MjModel) -> mujoco.MjData:
    """Simulation data for the minimal test model, with kinematics and contacts up to date."""
    data = mujoco.MjData(mj_model)
    mujoco.mj_forward(mj_model, data)
    return data


@pytest.fixture
def mock_core(mj_model: mujoco.MjModel, mj_data: mujoco.MjData) -> MagicMock:
    """A stub `PETPhysicsCore` exposing the model and data of the minimal test model.

    Additional attributes used by specific callbacks (e.g. `mj_model_timestep`, `n_mj_steps`) should be set
    explicitly by the tests that need them.
    """
    core = MagicMock()
    core.model = mj_model
    core.data = mj_data
    return core
