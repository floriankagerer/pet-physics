"""Tests for `GLFWCallbacks`."""

from types import SimpleNamespace
from typing import Callable
from unittest.mock import MagicMock

import mujoco
import pytest
from mujoco.glfw import glfw

from pet_physics.simulation.callbacks.viewer import glfw_callbacks as glfw_callbacks_module
from pet_physics.simulation.callbacks.viewer.glfw_callbacks import KEY_COMBINATION_TO_ACTION_NAME, GLFWCallbacks
from pet_physics.simulation.callbacks.viewer.wiggle_config import DEFAULT_VEL_X, DEFAULT_VEL_Y, DEFAULT_VEL_Z
from pet_physics.simulation.picklable_wrappers.mjv_camera import MjvCamera
from pet_physics.simulation.picklable_wrappers.mjv_option import MjvOption
from pet_physics.wrapper.mjt_vis_flag_wrapper import MjtVisFlag


@pytest.fixture
def callbacks(
    mock_core: MagicMock,
    mjv_scene: mujoco.MjvScene,
    mjv_camera: MjvCamera,
    mjv_option: MjvOption,
    window: object,
    mock_glfw: SimpleNamespace,
) -> GLFWCallbacks:
    """A `GLFWCallbacks` instance wired to mocked GLFW bindings and lightweight mujoco stand-ins."""
    return GLFWCallbacks(core=mock_core, scene=mjv_scene, camera=mjv_camera, options=mjv_option, window=window)


@pytest.fixture
def mock_move_camera(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Replaces `mujoco.mjv_moveCamera` so camera pan/zoom/rotate calls can be inspected precisely."""
    mock = MagicMock()
    monkeypatch.setattr(mujoco, "mjv_moveCamera", mock)
    return mock


def test_init_registers_all_glfw_callbacks(
    callbacks: GLFWCallbacks, mock_glfw: SimpleNamespace, window: object
) -> None:
    """The constructor should register scroll, mouse button, cursor position, and keyboard callbacks."""
    mock_glfw.set_scroll_callback.assert_called_once_with(window, callbacks.scroll)
    mock_glfw.set_mouse_button_callback.assert_called_once_with(window, callbacks.mouse_button)
    mock_glfw.set_cursor_pos_callback.assert_called_once_with(window, callbacks.mouse_move)
    mock_glfw.set_key_callback.assert_called_once_with(window, callbacks.keyboard)


def test_detect_pressed_keys_reports_only_relevant_keys(
    callbacks: GLFWCallbacks, press_keys: Callable[..., None], window: object
) -> None:
    """`detect_pressed_keys` should report the pressed state for exactly the keys used by registered actions."""
    expected_keys = {key for combination in KEY_COMBINATION_TO_ACTION_NAME for key in combination}
    press_keys(glfw.KEY_Q)

    pressed = callbacks.detect_pressed_keys(window)

    assert set(pressed.keys()) == expected_keys
    assert pressed[glfw.KEY_Q] is True
    assert all(value is False for key, value in pressed.items() if key != glfw.KEY_Q)


def test_keyboard_reset_core_action(
    callbacks: GLFWCallbacks, press_keys: Callable[..., None], mock_core: MagicMock, window: object
) -> None:
    """Pressing 'R' should reset the simulation core."""
    press_keys(glfw.KEY_R)

    callbacks.keyboard(window, glfw.KEY_R, 0, glfw.PRESS, 0)

    mock_core.reset.assert_called_once()


def test_keyboard_request_close_window_action(
    callbacks: GLFWCallbacks, press_keys: Callable[..., None], mock_glfw: SimpleNamespace, window: object
) -> None:
    """Pressing 'Q' should request the window to close."""
    press_keys(glfw.KEY_Q)

    callbacks.keyboard(window, glfw.KEY_Q, 0, glfw.PRESS, 0)

    mock_glfw.set_window_should_close.assert_called_once_with(window, 1)


@pytest.mark.parametrize(
    ("toggle_key", "flags"),
    [
        (glfw.KEY_T, (MjtVisFlag.TRANSPARENT,)),
        (glfw.KEY_C, (MjtVisFlag.CONTACT_POINT, MjtVisFlag.CONTACT_FORCE)),
    ],
)
def test_keyboard_toggle_actions_flip_visualization_flags(
    callbacks: GLFWCallbacks,
    press_keys: Callable[..., None],
    mjv_option: MjvOption,
    toggle_key: int,
    flags: tuple,
    window: object,
) -> None:
    """Pressing 'T' or 'C' should flip the corresponding visualization flags."""
    flags_before = [mjv_option.flags[flag] for flag in flags]
    press_keys(toggle_key)

    callbacks.keyboard(window, toggle_key, 0, glfw.PRESS, 0)

    for flag, before in zip(flags, flags_before):
        assert mjv_option.flags[flag] == (not before)


def test_keyboard_set_body_velocities_action(
    callbacks: GLFWCallbacks, press_keys: Callable[..., None], mock_core: MagicMock, window: object
) -> None:
    """Pressing 'S' should apply the configured wiggle velocities to the first non-static body."""
    press_keys(glfw.KEY_S)

    callbacks.keyboard(window, glfw.KEY_S, 0, glfw.PRESS, 0)

    assert mock_core.data.qvel[0] == DEFAULT_VEL_X
    assert mock_core.data.qvel[1] == DEFAULT_VEL_Y
    assert mock_core.data.qvel[2] == DEFAULT_VEL_Z


@pytest.mark.parametrize(
    ("velocity_keys", "qvel_index", "expected_velocity"),
    [
        ((glfw.KEY_1, glfw.KEY_UP), 0, DEFAULT_VEL_X + 2),
        ((glfw.KEY_1, glfw.KEY_DOWN), 0, DEFAULT_VEL_X - 2),
        ((glfw.KEY_2, glfw.KEY_UP), 1, DEFAULT_VEL_Y + 2),
        ((glfw.KEY_2, glfw.KEY_DOWN), 1, DEFAULT_VEL_Y - 2),
        ((glfw.KEY_3, glfw.KEY_UP), 2, DEFAULT_VEL_Z + 2),
        ((glfw.KEY_3, glfw.KEY_DOWN), 2, DEFAULT_VEL_Z - 2),
    ],
)
def test_keyboard_velocity_change_action_applies_on_next_set_body_velocities(
    callbacks: GLFWCallbacks,
    press_keys: Callable[..., None],
    mock_core: MagicMock,
    velocity_keys: tuple,
    qvel_index: int,
    expected_velocity: int,
    window: object,
) -> None:
    """Changing a wiggle velocity and then setting body velocities should apply the updated value."""
    press_keys(*velocity_keys)
    callbacks.keyboard(window, velocity_keys[0], 0, glfw.PRESS, 0)

    press_keys(glfw.KEY_S)
    callbacks.keyboard(window, glfw.KEY_S, 0, glfw.PRESS, 0)

    assert mock_core.data.qvel[qvel_index] == expected_velocity


def test_keyboard_ignores_unregistered_key(
    callbacks: GLFWCallbacks,
    press_keys: Callable[..., None],
    mock_core: MagicMock,
    mock_glfw: SimpleNamespace,
    window: object,
) -> None:
    """Pressing a key that is not part of any registered combination should trigger no action."""
    press_keys(glfw.KEY_A)

    callbacks.keyboard(window, glfw.KEY_A, 0, glfw.PRESS, 0)

    mock_core.reset.assert_not_called()
    mock_glfw.set_window_should_close.assert_not_called()


def test_keyboard_triggers_every_satisfied_combination(
    callbacks: GLFWCallbacks,
    press_keys: Callable[..., None],
    mock_core: MagicMock,
    mock_glfw: SimpleNamespace,
    window: object,
) -> None:
    """All key combinations whose keys are pressed should trigger, not just the first match."""
    press_keys(glfw.KEY_Q, glfw.KEY_R)

    callbacks.keyboard(window, glfw.KEY_Q, 0, glfw.PRESS, 0)

    mock_core.reset.assert_called_once()
    mock_glfw.set_window_should_close.assert_called_once_with(window, 1)


def test_scroll_zooms_camera_with_scaled_yoffset(
    callbacks: GLFWCallbacks,
    mock_move_camera: MagicMock,
    mjv_camera: MjvCamera,
    mj_model: mujoco.MjModel,
    window: object,
) -> None:
    """Scrolling should zoom the camera by `-0.05 * yoffset`."""
    callbacks.scroll(window, xoffset=0.0, yoffset=2.0)

    mock_move_camera.assert_called_once_with(mj_model, mujoco.mjtMouse.mjMOUSE_ZOOM, 0.0, -0.1, mjv_camera)


def test_mouse_button_updates_module_button_state_and_queries_cursor_position(
    callbacks: GLFWCallbacks, mock_glfw: SimpleNamespace, window: object
) -> None:
    """`mouse_button` should update the tracked left/middle/right button state and query the cursor position."""
    mock_glfw.get_mouse_button.side_effect = lambda _window, button: (
        glfw.PRESS if button == glfw.MOUSE_BUTTON_LEFT else glfw.RELEASE
    )

    callbacks.mouse_button(window, glfw.MOUSE_BUTTON_LEFT, glfw.PRESS, 0)

    assert glfw_callbacks_module.button_left is True
    assert glfw_callbacks_module.button_middle is False
    assert glfw_callbacks_module.button_right is False
    mock_glfw.get_cursor_pos.assert_called_once_with(window)


def test_mouse_move_without_buttons_pressed_tracks_position_but_does_not_move_camera(
    callbacks: GLFWCallbacks,
    mock_move_camera: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    window: object,
) -> None:
    """With no mouse button pressed, `mouse_move` should track the cursor position but not move the camera."""
    monkeypatch.setattr(glfw_callbacks_module, "button_left", False)
    monkeypatch.setattr(glfw_callbacks_module, "button_middle", False)
    monkeypatch.setattr(glfw_callbacks_module, "button_right", False)
    monkeypatch.setattr(glfw_callbacks_module, "lastx", 0.0)
    monkeypatch.setattr(glfw_callbacks_module, "lasty", 0.0)

    callbacks.mouse_move(window, 120.0, 80.0)

    mock_move_camera.assert_not_called()
    assert glfw_callbacks_module.lastx == 120.0
    assert glfw_callbacks_module.lasty == 80.0


@pytest.mark.parametrize(
    ("button_left", "button_middle", "button_right", "shift_pressed", "expected_action"),
    [
        (True, False, False, False, mujoco.mjtMouse.mjMOUSE_ROTATE_V),
        (True, False, False, True, mujoco.mjtMouse.mjMOUSE_ROTATE_H),
        (False, False, True, False, mujoco.mjtMouse.mjMOUSE_MOVE_V),
        (False, False, True, True, mujoco.mjtMouse.mjMOUSE_MOVE_H),
        (False, True, False, False, mujoco.mjtMouse.mjMOUSE_ZOOM),
    ],
)
def test_mouse_move_selects_camera_action_from_buttons_and_shift(
    callbacks: GLFWCallbacks,
    mock_move_camera: MagicMock,
    mock_glfw: SimpleNamespace,
    monkeypatch: pytest.MonkeyPatch,
    mjv_camera: MjvCamera,
    mj_model: mujoco.MjModel,
    window: object,
    button_left: bool,
    button_middle: bool,
    button_right: bool,
    shift_pressed: bool,
    expected_action: int,
) -> None:
    """`mouse_move` should pick the MuJoCo mouse action matching the pressed buttons and shift modifier."""
    monkeypatch.setattr(glfw_callbacks_module, "button_left", button_left)
    monkeypatch.setattr(glfw_callbacks_module, "button_middle", button_middle)
    monkeypatch.setattr(glfw_callbacks_module, "button_right", button_right)
    monkeypatch.setattr(glfw_callbacks_module, "lastx", 0.0)
    monkeypatch.setattr(glfw_callbacks_module, "lasty", 0.0)
    mock_glfw.get_window_size.return_value = (800, 600)
    shift_keys = {glfw.KEY_LEFT_SHIFT, glfw.KEY_RIGHT_SHIFT} if shift_pressed else set()
    mock_glfw.get_key.side_effect = lambda _window, key: glfw.PRESS if key in shift_keys else glfw.RELEASE

    callbacks.mouse_move(window, 100.0, 60.0)

    mock_move_camera.assert_called_once_with(mj_model, expected_action, 100.0 / 600, 60.0 / 600, mjv_camera)
