"""Tests for `OverlayUpdater`."""

from unittest.mock import MagicMock

import mujoco
import pytest

from pet_physics.simulation.callbacks.viewer import overlay_updater as overlay_updater_module
from pet_physics.simulation.callbacks.viewer.overlay_updater import GridPosition, OverlayUpdater
from pet_physics.simulation.callbacks.viewer.wiggle_config import WiggleConfig

_MODEL_XML = """
<mujoco>
  <worldbody>
    <geom type="plane" size="1 1 0.1" />
  </worldbody>
</mujoco>
"""


@pytest.fixture
def data() -> mujoco.MjData:
    """Simulation data with a fixed simulation time for deterministic overlay text."""
    model = mujoco.MjModel.from_xml_string(_MODEL_XML)
    data = mujoco.MjData(model)
    data.time = 1.5
    return data


@pytest.fixture
def mock_mjr_overlay(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Replaces `mujoco.mjr_overlay` so overlay content can be inspected without a real render context."""
    mock = MagicMock()
    monkeypatch.setattr(overlay_updater_module.mujoco, "mjr_overlay", mock)
    return mock


def _overlay_texts_by_grid_position(mock_mjr_overlay: MagicMock) -> dict:
    """Builds a mapping of grid position value to (label_text, value_text) from recorded `mjr_overlay` calls."""
    return {call.args[1]: (call.args[3], call.args[4]) for call in mock_mjr_overlay.call_args_list}


def test_new_overlay_updater_has_empty_overlay() -> None:
    """A freshly constructed `OverlayUpdater` should have an empty overlay."""
    assert OverlayUpdater().overlay == {}


def test_clear_overlay_resets_overlay_to_empty_dict() -> None:
    """`clear_overlay` should leave the overlay as an empty dict."""
    updater = OverlayUpdater()

    updater.clear_overlay()

    assert updater.overlay == {}


def test_update_overlay_always_includes_static_controls(mock_mjr_overlay: MagicMock, data: mujoco.MjData) -> None:
    """The bottom-left and bottom-right control hints should always be rendered."""
    updater = OverlayUpdater()

    updater.update_overlay(
        model=MagicMock(),
        data=data,
        viewport=MagicMock(),
        context=MagicMock(),
        callback_related={},
        simulation_status={},
    )

    texts = _overlay_texts_by_grid_position(mock_mjr_overlay)
    bottom_left_labels, bottom_left_values = texts[GridPosition.BOTTOM_LEFT.value]
    assert bottom_left_labels == "Quit\nRestart\nStart\nTime\n"
    assert bottom_left_values == "q\nr\ns\n%.2f\n" % data.time

    bottom_right_labels, bottom_right_values = texts[GridPosition.BOTTOM_RIGHT.value]
    assert bottom_right_labels == "Toggle transparency\nToggle contact forces\n"
    assert bottom_right_values == "t\nc\n"

    assert GridPosition.TOP_LEFT.value not in texts
    assert GridPosition.TOP_RIGHT.value not in texts


def test_update_overlay_includes_wiggle_velocities_when_wiggle_callback_present(
    mock_mjr_overlay: MagicMock, data: mujoco.MjData
) -> None:
    """Wiggle velocity entries should be added to the top-left position when a wiggle callback is provided."""
    updater = OverlayUpdater()
    wiggle_config = WiggleConfig()

    updater.update_overlay(
        model=MagicMock(),
        data=data,
        viewport=MagicMock(),
        context=MagicMock(),
        callback_related={"wiggle": wiggle_config},
        simulation_status={},
    )

    texts = _overlay_texts_by_grid_position(mock_mjr_overlay)
    top_left_labels, top_left_values = texts[GridPosition.TOP_LEFT.value]
    assert "vel x ('1' + up/down)" in top_left_labels
    assert "vel y ('2' + up/down)" in top_left_labels
    assert "vel z ('3' + up/down)" in top_left_labels
    assert top_left_values == "%.2f\n%.2f\n%.2f\n" % (wiggle_config.vel_x, wiggle_config.vel_y, wiggle_config.vel_z)


def test_update_overlay_includes_palletized_notice_when_status_flag_set(
    mock_mjr_overlay: MagicMock, data: mujoco.MjData
) -> None:
    """The 'all items palletized' notice should appear in the top-right position when the status flag is set."""
    updater = OverlayUpdater()

    updater.update_overlay(
        model=MagicMock(),
        data=data,
        viewport=MagicMock(),
        context=MagicMock(),
        callback_related={},
        simulation_status={"all_items_palletized": True},
    )

    texts = _overlay_texts_by_grid_position(mock_mjr_overlay)
    assert texts[GridPosition.TOP_RIGHT.value] == ("All items palletized\n", "\n")


@pytest.mark.parametrize("simulation_status", [{}, {"all_items_palletized": False}])
def test_update_overlay_omits_palletized_notice_when_status_flag_not_set(
    mock_mjr_overlay: MagicMock, data: mujoco.MjData, simulation_status: dict
) -> None:
    """The 'all items palletized' notice should be omitted when the status flag is absent or `False`."""
    updater = OverlayUpdater()

    updater.update_overlay(
        model=MagicMock(),
        data=data,
        viewport=MagicMock(),
        context=MagicMock(),
        callback_related={},
        simulation_status=simulation_status,
    )

    texts = _overlay_texts_by_grid_position(mock_mjr_overlay)
    assert GridPosition.TOP_RIGHT.value not in texts
