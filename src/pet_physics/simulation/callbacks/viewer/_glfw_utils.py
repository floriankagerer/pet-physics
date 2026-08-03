"""Utility functions for working with GLFW."""

from mujoco.glfw import glfw


def is_key_pressed(window: glfw._GLFWwindow, key: int) -> bool:
    """Checks if a specific key is currently pressed in the GLFW window.

    Args:
        window: The GLFW window to check for key press.
        key: The key code to check (e.g., glfw.KEY_A).

    Returns:
        `True` if the key is pressed, `False` otherwise.
    """
    return glfw.get_key(window, key) == glfw.PRESS
