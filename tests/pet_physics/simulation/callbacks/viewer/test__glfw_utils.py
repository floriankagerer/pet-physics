"""Tests for GLFW key-state utilities."""

from collections.abc import Callable

from mujoco.glfw import glfw

from pet_physics.simulation.callbacks.viewer._glfw_utils import is_key_pressed


def test_is_key_pressed_returns_true_for_a_pressed_key(press_keys: Callable[..., None]) -> None:
    """Should return `True` when the queried key is reported as pressed."""
    press_keys(glfw.KEY_A)

    assert is_key_pressed(window=object(), key=glfw.KEY_A) is True


def test_is_key_pressed_returns_false_for_a_released_key(press_keys: Callable[..., None]) -> None:
    """Should return `False` when the queried key is not among the pressed keys."""
    press_keys(glfw.KEY_A)

    assert is_key_pressed(window=object(), key=glfw.KEY_B) is False
