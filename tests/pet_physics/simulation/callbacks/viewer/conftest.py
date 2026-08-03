"""Shared fixtures for `simulation.callbacks.viewer` tests."""

from __future__ import annotations

from collections.abc import Callable
from types import SimpleNamespace
from unittest.mock import MagicMock

import mujoco
import pytest
from mujoco.glfw import glfw

from pet_physics.simulation.picklable_wrappers.mjv_camera import MjvCamera
from pet_physics.simulation.picklable_wrappers.mjv_option import MjvOption

_MINIMAL_MODEL_XML = """
<mujoco model="viewer_callback_test_model">
  <worldbody>
    <geom name="ground" type="plane" size="1 1 0.1" />
    <body name="box" pos="0 0 0.2">
      <freejoint />
      <geom name="box_geom" type="box" size="0.05 0.05 0.05" mass="1" />
    </body>
  </worldbody>
</mujoco>
"""

_MOCKED_GLFW_FUNCTION_NAMES = (
    "set_scroll_callback",
    "set_mouse_button_callback",
    "set_cursor_pos_callback",
    "set_key_callback",
    "get_mouse_button",
    "get_cursor_pos",
    "get_window_size",
    "get_key",
    "set_window_should_close",
)


@pytest.fixture
def mj_model() -> mujoco.MjModel:
    """A minimal MuJoCo model with a single free body for viewer callback tests."""
    return mujoco.MjModel.from_xml_string(_MINIMAL_MODEL_XML)


@pytest.fixture
def mj_data(mj_model: mujoco.MjModel) -> mujoco.MjData:
    """Simulation data for the minimal test model."""
    return mujoco.MjData(mj_model)


@pytest.fixture
def mjv_scene(mj_model: mujoco.MjModel) -> mujoco.MjvScene:
    """A `mujoco.MjvScene` sized for the minimal test model."""
    return mujoco.MjvScene(mj_model, maxgeom=10)


@pytest.fixture
def mjv_camera() -> MjvCamera:
    """A picklable camera wrapper instance."""
    return MjvCamera()


@pytest.fixture
def mjv_option() -> MjvOption:
    """A picklable visualization options wrapper instance."""
    return MjvOption()


@pytest.fixture
def mock_core(mj_model: mujoco.MjModel, mj_data: mujoco.MjData) -> MagicMock:
    """A stub `PETPhysicsCore` exposing only the attributes used by the viewer callbacks."""
    core = MagicMock()
    core.model = mj_model
    core.data = mj_data
    return core


@pytest.fixture
def window() -> object:
    """A sentinel window handle; all GLFW interactions are mocked in these tests."""
    return object()


@pytest.fixture
def mock_glfw(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Replaces the GLFW functions used by the viewer callbacks with mocks.

    The mocks are installed directly on the shared `glfw` module so that every module importing it
    (`glfw_callbacks` and `_glfw_utils`) observes the same patched behaviour.

    Args:
        monkeypatch: The pytest monkeypatch fixture.

    Returns:
        A namespace exposing the mocked functions by name.
    """
    mocks = {name: MagicMock(name=name) for name in _MOCKED_GLFW_FUNCTION_NAMES}
    for name, mock in mocks.items():
        monkeypatch.setattr(glfw, name, mock)

    mocks["get_key"].return_value = glfw.RELEASE
    mocks["get_window_size"].return_value = (800, 600)

    return SimpleNamespace(**mocks)


@pytest.fixture
def press_keys(mock_glfw: SimpleNamespace) -> Callable[..., None]:
    """Returns a helper that configures `glfw.get_key` to report only the given keys as pressed."""

    def _press(*keys: int) -> None:
        pressed = set(keys)
        mock_glfw.get_key.side_effect = lambda _window, key: glfw.PRESS if key in pressed else glfw.RELEASE

    return _press
