"""Tests for `ViewerCallback`."""

from unittest.mock import MagicMock

import mujoco
import numpy as np
import pytest
from mujoco.glfw import glfw

from pet_physics.data_model.simulation.camera_view import CameraView
from pet_physics.simulation.callbacks import viewer_callback as viewer_callback_module
from pet_physics.simulation.callbacks.viewer_callback import ViewerCallback
from pet_physics.simulation.picklable_wrappers.mjv_camera import MjvCamera
from pet_physics.simulation.picklable_wrappers.mjv_option import MjvOption


@pytest.fixture
def mock_glfw_window_instance() -> MagicMock:
    """A stand-in for a `GLFWWindow`, exposing only the `window` attribute used by `ViewerCallback`."""
    instance = MagicMock()
    instance.window = MagicMock(name="raw_glfw_window_handle")
    return instance


@pytest.fixture
def mock_glfw_callbacks_instance() -> MagicMock:
    """A stand-in for `GLFWCallbacks`, exposing only the `_wiggle_config` attribute used by `ViewerCallback`."""
    instance = MagicMock()
    instance._wiggle_config = "sentinel-wiggle-config"
    return instance


@pytest.fixture
def patched_viewer_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    mock_glfw_window_instance: MagicMock,
    mock_glfw_callbacks_instance: MagicMock,
) -> dict:
    """Replaces every external rendering/windowing dependency of `ViewerCallback` with mocks.

    Returns:
        A dict exposing the mocked `GLFWWindow`, `GLFWCallbacks`, and `OverlayUpdater` classes.
    """
    mock_glfw_window_class = MagicMock(return_value=mock_glfw_window_instance)
    mock_glfw_callbacks_class = MagicMock(return_value=mock_glfw_callbacks_instance)
    mock_overlay_updater_class = MagicMock()

    monkeypatch.setattr(viewer_callback_module, "GLFWWindow", mock_glfw_window_class)
    monkeypatch.setattr(viewer_callback_module, "GLFWCallbacks", mock_glfw_callbacks_class)
    monkeypatch.setattr(viewer_callback_module, "OverlayUpdater", mock_overlay_updater_class)
    monkeypatch.setattr(viewer_callback_module, "visualize_contacts_and_forces", MagicMock())
    monkeypatch.setattr(glfw, "init", MagicMock())
    monkeypatch.setattr(glfw, "get_framebuffer_size", MagicMock(return_value=(800, 600)))
    monkeypatch.setattr(glfw, "swap_buffers", MagicMock())
    monkeypatch.setattr(glfw, "poll_events", MagicMock())
    monkeypatch.setattr(glfw, "window_should_close", MagicMock(return_value=False))
    monkeypatch.setattr(glfw, "terminate", MagicMock())
    monkeypatch.setattr(mujoco, "MjvScene", MagicMock())
    monkeypatch.setattr(mujoco, "MjrContext", MagicMock())
    monkeypatch.setattr(mujoco, "mjv_defaultCamera", MagicMock())
    monkeypatch.setattr(mujoco, "mjv_defaultOption", MagicMock())
    monkeypatch.setattr(mujoco, "mjv_updateScene", MagicMock())
    monkeypatch.setattr(mujoco, "mjr_render", MagicMock())

    return {
        "GLFWWindow": mock_glfw_window_class,
        "GLFWCallbacks": mock_glfw_callbacks_class,
        "OverlayUpdater": mock_overlay_updater_class,
    }


@pytest.fixture
def mock_core_with_step_info(mock_core: MagicMock) -> MagicMock:
    """The shared mock core configured with the step-count attributes required by `call_on_every_nth_mj_step`."""
    mock_core.mj_step_index_final = 10
    mock_core.mj_steps_per_core_run_timestep = 5
    return mock_core


@pytest.fixture
def initialized_viewer(patched_viewer_dependencies: dict, mock_core_with_step_info: MagicMock) -> ViewerCallback:
    """A `ViewerCallback` that has completed its (mocked) initialization."""
    viewer = ViewerCallback()
    viewer.init_callback(mock_core_with_step_info)
    return viewer


def test_init_callback_sets_up_the_viewer_and_returns_step_indices(
    patched_viewer_dependencies: dict, mock_core_with_step_info: MagicMock
) -> None:
    """The first `init_callback` call should build the window, callbacks, and overlay, and return step indices."""
    viewer = ViewerCallback()

    relevant_indices = viewer.init_callback(mock_core_with_step_info)

    assert relevant_indices == [0, 5, 10]
    patched_viewer_dependencies["GLFWWindow"].assert_called_once_with(
        width=1920, height=1080, title="PETPhysics-Viewer", monitor=None, share=None
    )
    patched_viewer_dependencies["OverlayUpdater"].assert_called_once()

    callbacks_kwargs = patched_viewer_dependencies["GLFWCallbacks"].call_args.kwargs
    assert callbacks_kwargs["core"] is mock_core_with_step_info
    assert callbacks_kwargs["scene"] is mujoco.MjvScene.return_value
    assert callbacks_kwargs["window"] is viewer.visualization_window
    assert isinstance(callbacks_kwargs["camera"], MjvCamera)
    assert isinstance(callbacks_kwargs["options"], MjvOption)


def test_init_callback_is_a_no_op_on_subsequent_calls(
    patched_viewer_dependencies: dict, mock_core_with_step_info: MagicMock
) -> None:
    """Calling `init_callback` a second time should not rebuild the viewer and should return `None`."""
    viewer = ViewerCallback()
    viewer.init_callback(mock_core_with_step_info)

    result = viewer.init_callback(mock_core_with_step_info)

    assert result is None
    patched_viewer_dependencies["GLFWWindow"].assert_called_once()


def test_visualization_window_returns_the_raw_glfw_window_handle(
    initialized_viewer: ViewerCallback, mock_glfw_window_instance: MagicMock
) -> None:
    """Should return the raw window handle wrapped by the `GLFWWindow`."""
    assert initialized_viewer.visualization_window is mock_glfw_window_instance.window


def test_wiggle_config_delegates_to_the_glfw_callbacks(initialized_viewer: ViewerCallback) -> None:
    """Should return the wiggle configuration owned by the installed `GLFWCallbacks`."""
    assert initialized_viewer.wiggle_config == "sentinel-wiggle-config"


def test_set_view_of_camera_configures_the_camera_used_during_rendering(initialized_viewer: ViewerCallback) -> None:
    """The applied camera view should be forwarded to the scene update on the next `update` call."""
    camera_view = CameraView(azimuth=10.0, elevation=20.0, distance=3.0, lookat=np.array([1.0, 2.0, 3.0]))

    initialized_viewer.set_view_of_camera(camera_view)
    initialized_viewer.update(viewport=MagicMock())

    used_camera = mujoco.mjv_updateScene.call_args.args[4]
    assert used_camera.azimuth == 10.0
    assert used_camera.elevation == 20.0
    assert used_camera.distance == 3.0
    assert list(used_camera.lookat) == [1.0, 2.0, 3.0]


def test_update_renders_the_scene_into_the_given_viewport(initialized_viewer: ViewerCallback) -> None:
    """`update` should render the scene into the provided viewport."""
    viewport = MagicMock()

    initialized_viewer.update(viewport)

    mujoco.mjr_render.assert_called_once()
    assert mujoco.mjr_render.call_args.args[0] is viewport


def test_update_refreshes_the_overlay_with_wiggle_and_palletizing_status(
    initialized_viewer: ViewerCallback, mock_core_with_step_info: MagicMock, patched_viewer_dependencies: dict
) -> None:
    """`update` should refresh the overlay with the current wiggle config and palletizing status."""
    mock_core_with_step_info.body_teleporter.are_all_body_teleports_applied = True
    viewport = MagicMock()

    initialized_viewer.update(viewport)

    overlay_instance = patched_viewer_dependencies["OverlayUpdater"].return_value
    overlay_instance.update_overlay.assert_called_once_with(
        model=mock_core_with_step_info.model,
        data=mock_core_with_step_info.data,
        viewport=viewport,
        context=mujoco.MjrContext.return_value,
        callback_related={"wiggle": "sentinel-wiggle-config"},
        simulation_status={"all_items_palletized": True},
    )


def test_call_swaps_buffers_polls_events_and_reports_close_state(
    initialized_viewer: ViewerCallback,
) -> None:
    """`call` should render, swap buffers, poll events, and return the window's close state."""
    initialized_viewer.update = MagicMock()
    glfw.window_should_close.return_value = True

    result = initialized_viewer.call()

    assert result is True
    initialized_viewer.update.assert_called_once()
    glfw.swap_buffers.assert_called_once_with(initialized_viewer.visualization_window)
    glfw.poll_events.assert_called_once()


def test_post_run_and_reset_do_not_raise(initialized_viewer: ViewerCallback) -> None:
    """`post_run` and `reset` should be safe no-ops."""
    initialized_viewer.post_run()
    initialized_viewer.reset()
