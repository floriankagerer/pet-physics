"""GLFW callback implementations for interactive MuJoCo simulation windows."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import mujoco
import structlog
from mujoco.glfw import glfw

from pet_physics.simulation.callbacks.viewer._glfw_utils import is_key_pressed
from pet_physics.simulation.callbacks.viewer.visualization_settings import (
    toggle_transparency_boxes,
    toggle_visibility_contact_forces,
    toggle_visibility_contact_points,
)
from pet_physics.simulation.callbacks.viewer.wiggle_config import WiggleConfig
from pet_physics.simulation.picklable_wrappers.mjv_camera import MjvCamera
from pet_physics.simulation.picklable_wrappers.mjv_option import MjvOption

if TYPE_CHECKING:
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore

logger = structlog.get_logger(__name__)

# For callback functions
button_left = False
button_middle = False
button_right = False
lastx = 0
lasty = 0


KEY_COMBINATION_TO_ACTION_NAME = {
    (glfw.KEY_1, glfw.KEY_UP): "increase_velocity_x",
    (glfw.KEY_1, glfw.KEY_DOWN): "decrease_velocity_x",
    (glfw.KEY_2, glfw.KEY_UP): "increase_velocity_y",
    (glfw.KEY_2, glfw.KEY_DOWN): "decrease_velocity_y",
    (glfw.KEY_3, glfw.KEY_UP): "increase_velocity_z",
    (glfw.KEY_3, glfw.KEY_DOWN): "decrease_velocity_z",
    (glfw.KEY_Q,): "request_close_window",
    (glfw.KEY_R,): "reset_core",
    (glfw.KEY_S,): "set_body_velocities",
    (glfw.KEY_T,): "toggle_transparency_boxes",
    (glfw.KEY_C,): "toggle_visibility_contact_points_and_forces",
}


def _set_body_velocities_to_first_non_static_body(mj_data: mujoco.MjData, wiggle_config: WiggleConfig) -> None:
    """Sets the velocities of the first non-static body in the simulation to the configured wiggle velocities.

    Args:
        mj_data: The MuJoCo simulation data.
        wiggle_config: The configuration containing the desired velocities.
    """
    mj_data.qvel[0] = wiggle_config.vel_x
    mj_data.qvel[1] = wiggle_config.vel_y
    mj_data.qvel[2] = wiggle_config.vel_z


class GLFWCallbacks:
    """Contains callbacks for a GLFW window used with a MuJoCo simulation.

    Handles mouse scrolling, button presses, mouse movement, and keyboard input
    to allow interactive control of the simulation camera and body velocities.
    """

    def __init__(
        self,
        core: PETPhysicsCore,
        scene: mujoco.MjvScene,
        camera: MjvCamera,
        options: MjvOption,
        window: glfw._GLFWwindow,
    ) -> None:
        """Initializes the GLFW callbacks.

        Args:
            core: The PETPhysics core of the simulation.
            scene: The MuJoCo visualization scene.
            camera: The picklable camera wrapper.
            options: The picklable visualization options wrapper.
            window: The GLFW window to register the callbacks with.
        """
        self._core = core
        self._scene = scene
        self._camera = camera
        self._options = options
        self._window = window
        self._register_glfw_callbacks(self._window)

        self._wiggle_config = WiggleConfig()

        self._action_registry = self._build_action_registry()
        """A mapping of key combinations to their corresponding action functions."""
        self._keys_relevant_to_actions = {key for key_combination in self._action_registry for key in key_combination}
        """A set of all keys that are relevant to the registered actions."""

    @property
    def _data(self) -> mujoco.MjData:
        """The MuJoCo simulation data of the core."""
        return self._core.data

    @property
    def _model(self) -> mujoco.MjModel:
        """The MuJoCo model of the core."""
        return self._core.model

    def _register_glfw_callbacks(self, window: glfw._GLFWwindow) -> None:
        """Registers the GLFW callbacks for mouse and keyboard events.

        Args:
            window: The GLFW window to register the callbacks with.
        """
        glfw.set_scroll_callback(window, self.scroll)
        glfw.set_mouse_button_callback(window, self.mouse_button)
        glfw.set_cursor_pos_callback(window, self.mouse_move)
        glfw.set_key_callback(window, self.keyboard)

    def _get_mapping_action_name_to_function(self) -> dict[str, Callable]:
        """Returns a mapping from action names to their corresponding functions.

        Returns:
            A dictionary mapping action names to callable functions.
        """
        return {
            "increase_velocity_x": lambda: self._wiggle_config.increase_velocity_x(),
            "decrease_velocity_x": lambda: self._wiggle_config.decrease_velocity_x(),
            "increase_velocity_y": lambda: self._wiggle_config.increase_velocity_y(),
            "decrease_velocity_y": lambda: self._wiggle_config.decrease_velocity_y(),
            "increase_velocity_z": lambda: self._wiggle_config.increase_velocity_z(),
            "decrease_velocity_z": lambda: self._wiggle_config.decrease_velocity_z(),
            "request_close_window": lambda: glfw.set_window_should_close(self._window, 1),
            "reset_core": lambda: self._core.reset(),
            "set_body_velocities": lambda: _set_body_velocities_to_first_non_static_body(
                mj_data=self._data, wiggle_config=self._wiggle_config
            ),
            "toggle_transparency_boxes": lambda: toggle_transparency_boxes(self._options),
            "toggle_visibility_contact_points_and_forces": lambda: (
                toggle_visibility_contact_points(self._options),
                toggle_visibility_contact_forces(self._options),
            ),
        }

    def _build_action_registry(self) -> dict[frozenset[int], Callable]:
        """Builds a registry mapping key combinations to action functions.

        Returns:
            A dictionary mapping frozensets of key codes to action functions.
        """
        action_registry = {}
        action_name_to_function = self._get_mapping_action_name_to_function()

        for keys, action_name in KEY_COMBINATION_TO_ACTION_NAME.items():
            action = action_name_to_function.get(action_name, None)
            if action is None:
                logger.warning(f"Action '{action_name}' not found. Ignoring this key combination.")
                continue

            action_registry[frozenset(keys)] = action

        sorted_action_registry = dict(sorted(action_registry.items(), key=lambda item: len(item[0]), reverse=True))

        return sorted_action_registry

    def scroll(self, window, xoffset, yoffset) -> None:
        """Handles mouse scroll events to zoom the camera.

        Args:
            window: The GLFW window receiving the event.
            xoffset: The horizontal scroll offset.
            yoffset: The vertical scroll offset.
        """
        mouse_zoom_action = mujoco.mjtMouse.mjMOUSE_ZOOM
        mujoco.mjv_moveCamera(self._model, mouse_zoom_action, 0.0, -0.05 * yoffset, self._camera)

    def mouse_button(self, window, button, act, mods) -> None:
        """Handles mouse button events to track button state.

        Args:
            window: The GLFW window receiving the event.
            button: The mouse button that was pressed or released.
            act: The action (press or release).
            mods: Modifier keys held during the event.
        """
        # update button state
        global button_left
        global button_middle
        global button_right

        button_left = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS
        button_middle = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS
        button_right = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS

        # update mouse position
        glfw.get_cursor_pos(window)

    def mouse_move(self, window, xpos, ypos) -> None:
        """Handles mouse movement events to rotate or pan the camera.

        Args:
            window: The GLFW window receiving the event.
            xpos: The new x-position of the cursor.
            ypos: The new y-position of the cursor.
        """
        # compute mouse displacement, save
        global lastx
        global lasty
        global button_left
        global button_middle
        global button_right

        dx = xpos - lastx
        dy = ypos - lasty
        lastx = xpos
        lasty = ypos

        # no buttons down: nothing to do
        if (not button_left) and (not button_middle) and (not button_right):
            return

        # get current window size
        width, height = glfw.get_window_size(window)

        # get shift key state
        PRESS_LEFT_SHIFT = glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
        PRESS_RIGHT_SHIFT = glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
        mod_shift = PRESS_LEFT_SHIFT or PRESS_RIGHT_SHIFT

        # determine action based on mouse button
        if button_right:
            if mod_shift:
                action = mujoco.mjtMouse.mjMOUSE_MOVE_H
            else:
                action = mujoco.mjtMouse.mjMOUSE_MOVE_V
        elif button_left:
            if mod_shift:
                action = mujoco.mjtMouse.mjMOUSE_ROTATE_H
            else:
                action = mujoco.mjtMouse.mjMOUSE_ROTATE_V
        else:
            action = mujoco.mjtMouse.mjMOUSE_ZOOM

        mujoco.mjv_moveCamera(self._model, action, dx / height, dy / height, self._camera)

    def detect_pressed_keys(self, window: glfw._GLFWwindow) -> dict[int, bool]:
        """Detects whether the keys that have a callback are pressed.

        Args:
            window: The GLFW window to query.

        Returns:
            A mapping of key codes to booleans indicating whether each key is currently pressed.
        """
        return {key: is_key_pressed(window, key) for key in self._keys_relevant_to_actions}

    def keyboard(self, window: glfw._GLFWwindow, key: int, scancode: int, act: int, mods: int) -> None:
        """Handles keyboard events to control simulation state and camera.

        Args:
            window: The GLFW window receiving the event.
            key: The keyboard key code that was pressed.
            scancode: The system-specific scancode of the key.
            act: The action (press, release, or repeat).
            mods: Modifier keys held during the event.
        """
        is_key_pressed = self.detect_pressed_keys(window)

        for key_combination, action_function in self._action_registry.items():
            if all(is_key_pressed.get(key, False) for key in key_combination):
                action_function()
