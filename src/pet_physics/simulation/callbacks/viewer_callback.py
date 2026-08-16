"""This callback is responsible for visualizing the simulation in an interactive viewer."""

from __future__ import annotations

from typing import TYPE_CHECKING

import mujoco
import numpy as np
import structlog
from mujoco.glfw import glfw

from pet_physics.data_model.simulation.camera_view import CameraView
from pet_physics.simulation.callbacks.base_callback import BaseCallback
from pet_physics.simulation.callbacks.viewer.glfw_callbacks import GLFWCallbacks
from pet_physics.simulation.callbacks.viewer.overlay_updater import OverlayUpdater
from pet_physics.simulation.callbacks.viewer.visualization_settings import visualize_contacts_and_forces
from pet_physics.simulation.picklable_wrappers.glfw_window import GLFWWindow
from pet_physics.simulation.picklable_wrappers.mjv_camera import MjvCamera
from pet_physics.simulation.picklable_wrappers.mjv_option import MjvOption

if TYPE_CHECKING:
    from pet_physics.simulation.callbacks.viewer.wiggle_config import WiggleConfig
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore


PRINT_CAMERA_CONFIG = False
"""Indicates whether the camera configuration is printed. Helpful for initializing the view."""

INITIAL_CAMERA_VIEW = CameraView(
    azimuth=56.890380859374986,
    elevation=-15.91253662109375,
    distance=1.873891724084047,
    lookat=np.array([0.2807653, -0.01319229, 0.44224963]),
)
"""The initial view of the camera."""

logger = structlog.get_logger(__name__)


class ViewerCallback(BaseCallback):
    """A callback for visualizing a MuJoCo simulation in an interactive viewer."""

    def __init__(self):
        """Set up the viewer callback."""
        super().__init__()

        # The following attributes are initialized in the `init_callback` method
        self._camera: MjvCamera | None = None
        """An abstract camera for the viewer."""
        self._options: MjvOption | None = None
        """Visualization options."""
        self._window: GLFWWindow | None = None
        """The render window."""
        self._scene: mujoco.MjvScene | None = None
        """The scene."""
        self._context: mujoco.MjrContext | None = None
        """The context."""
        self._callbacks_glfw: GLFWCallbacks | None = None
        """The callbacks for glfw."""
        self._viewer_overlay: OverlayUpdater | None = None
        """Is responsible for the information that is displayed in the GUI."""

        self._is_initialized = False
        """Indicates whether the current instance is initialized."""

    @property
    def wiggle_config(self) -> WiggleConfig:
        """The wiggle configuration used during simulation."""
        return self._callbacks_glfw._wiggle_config

    @property
    def visualization_window(self) -> glfw._GLFWwindow:
        """The window in which the simulation is visualized."""
        return self._window.window

    def init_callback(self, core: PETPhysicsCore) -> list[int] | None:
        """Set up the viewer for visualization before the first simulation step.

        In general, this method is called **before** the first `core.step()` call.

        Args:
            core: The core this callback is added to.

        Returns:
            The list of `mujoco.mj_step` call indices at which this callback is called.
        """
        # TODO: Unfortunately we don't have separate callbacks that would be called at the start of each process,
        #   so we have to employ this hack, that simulates the behavior, that the callback is only called once per
        #   instance.
        #   Note: it is possible we would have to handle this more carefully on systems that do multiprocessing
        if self._is_initialized:
            return None

        glfw.init()

        self._camera = MjvCamera()
        self._options = MjvOption()
        self._core = core
        self._window = self._init_glfw_window()
        self._viewer_overlay = OverlayUpdater()
        self._scene, self._context = self._init_visualization_data_structures(self.core)
        self._callbacks_glfw = GLFWCallbacks(
            core=core, scene=self._scene, camera=self._camera, options=self._options, window=self.visualization_window
        )
        self.set_view_of_camera(INITIAL_CAMERA_VIEW)
        visualize_contacts_and_forces(self.core.model, self._options)

        self._is_initialized = True

        relevant_mj_step_indices = self.call_on_every_nth_mj_step()
        return relevant_mj_step_indices

    def call(self) -> bool:
        """Render the current simulation frame and handle pending GUI events.

        Returns:
            `True` if the viewer window has been closed, `False` otherwise.
        """
        # get framebuffer viewport
        viewport_width, viewport_height = glfw.get_framebuffer_size(self.visualization_window)
        viewport = mujoco.MjrRect(0, 0, viewport_width, viewport_height)

        if PRINT_CAMERA_CONFIG:
            print(
                CameraView(
                    azimuth=self._camera.azimuth,
                    elevation=self._camera.elevation,
                    distance=self._camera.distance,
                    lookat=self._camera.lookat,
                )
            )

        self.update(viewport)
        logger.debug(f"current step: {self.core.n_mj_steps}")

        # swap OpenGL buffers (blocking call due to v-sync)
        glfw.swap_buffers(self.visualization_window)

        # process pending GUI events, call GLFW callbacks
        glfw.poll_events()

        return glfw.window_should_close(self.visualization_window)

    def post_run(self) -> None:
        """No-op post-run hook; no finalization is required for the viewer."""
        pass

    def reset(self) -> None:
        """No-op; the viewer state persists across simulation runs."""
        pass

    def _init_glfw_window(
        self,
        width: int = 1920,
        height: int = 1080,
        title: str = "PETPhysics-Viewer",
        monitor: glfw._GLFWmonitor | None = None,
        share: glfw._GLFWwindow | None = None,
    ) -> GLFWWindow:
        """Create and return a GLFW window configured for simulation visualization.

        Args:
            width: The width of the GLFW window in pixels.
            height: The height of the GLFW window in pixels.
            title: The title of the window.
            monitor: If `None`, the window is created in windowed mode. Otherwise, the window is created in full screen
                mode on the specified monitor.
            share: If not `None`, the new window shares OpenGL resources (textures, buffers) with the specified window.
                If `None`, no resources are shared.

        Returns:
            The configured `GLFWWindow` for simulation visualization.
        """
        return GLFWWindow(
            width=width,
            height=height,
            title=title,
            monitor=monitor,
            share=share,
        )

    def _init_visualization_data_structures(self, core: PETPhysicsCore) -> tuple[mujoco.MjvScene, mujoco.MjrContext]:
        """Build the scene and rendering context required for visualization.

        Args:
            core: The MuJoCo simulation core.

        Returns:
            A tuple (scene, context), where scene is the `MjvScene` and context is the `MjrContext`.
        """
        mujoco.mjv_defaultCamera(self._camera)
        mujoco.mjv_defaultOption(self._options)
        scene = mujoco.MjvScene(core.model, maxgeom=10000)
        context = mujoco.MjrContext(core.model, mujoco.mjtFontScale.mjFONTSCALE_150.value)

        return scene, context

    def _init_and_add_callbacks_glfw(
        self, core: PETPhysicsCore, scene: mujoco.MjvScene, camera: MjvCamera
    ) -> GLFWCallbacks:
        """Install GLFW mouse and keyboard callbacks.

        Args:
            core: The MuJoCo simulation core.
            scene: The scene.
            camera: The camera.

        Returns:
            The `GLFWCallbacks` instance registered with the viewer window.
        """
        callbacks_glfw = GLFWCallbacks(
            core=core, scene=scene, camera=camera, options=self._options, window=self.visualization_window
        )

        return callbacks_glfw

    def set_view_of_camera(self, camera_view: CameraView = INITIAL_CAMERA_VIEW) -> None:
        """Apply a camera configuration to position and orient the viewer.

        Args:
            camera_view: The `CameraView` instance defining the camera position and orientation.
        """
        self._camera.azimuth = camera_view.azimuth
        self._camera.elevation = camera_view.elevation
        self._camera.distance = camera_view.distance
        self._camera.lookat = camera_view.lookat

    def update(self, viewport: mujoco.MjrRect) -> None:
        """Refresh the rendered scene and overlay for the current simulation state.

        Args:
            viewport: The viewport.
        """
        self._update_scene(viewport)
        self._update_overlay(viewport)

    def _update_scene(self, viewport: mujoco.MjrRect) -> None:
        """Render the current simulation geometry into the viewport.

        Args:
            viewport: The viewport.
        """
        mujoco.mjv_updateScene(
            self.core.model,
            self.core.data,
            self._options._mjvoption,
            None,
            self._camera._mjvcamera,
            mujoco.mjtCatBit.mjCAT_ALL.value,
            self._scene,
        )
        mujoco.mjr_render(viewport, self._scene, self._context)

    def _update_overlay(self, viewport: mujoco.MjrRect) -> None:
        """Render the information overlay onto the current viewport.

        Args:
            viewport: The viewport.
        """
        self._viewer_overlay.update_overlay(
            model=self.core.model,
            data=self.core.data,
            viewport=viewport,
            context=self._context,
            callback_related={"wiggle": self.wiggle_config},
            simulation_status={"all_items_palletized": self.core.body_teleporter.are_all_body_teleports_applied},
        )

    def __del__(self):
        glfw.terminate()
