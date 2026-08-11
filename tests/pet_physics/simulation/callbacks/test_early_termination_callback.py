"""Tests for `EarlyTerminationIfAnyBoxTouchesFloorCallback`."""

from unittest.mock import MagicMock

import pytest

from pet_physics.simulation.callbacks.early_termination_callback import (
    EarlyTerminationIfAnyBoxTouchesFloorCallback,
)


@pytest.fixture
def callback() -> EarlyTerminationIfAnyBoxTouchesFloorCallback:
    """A callback with no body-to-size mapping configured yet."""
    return EarlyTerminationIfAnyBoxTouchesFloorCallback()


def test_body_name_to_size_mapping_raises_when_unset(
    callback: EarlyTerminationIfAnyBoxTouchesFloorCallback,
) -> None:
    """Accessing the mapping before it has been set should raise a `RuntimeError`."""
    with pytest.raises(RuntimeError):
        _ = callback.body_name_to_size_mapping


def test_body_name_to_size_mapping_setter_updates_the_mapping(
    callback: EarlyTerminationIfAnyBoxTouchesFloorCallback,
) -> None:
    """Setting the mapping should make it available through the getter."""
    mapping = {"box_a": (0.1, 0.1, 0.1)}

    callback.body_name_to_size_mapping = mapping

    assert callback.body_name_to_size_mapping == mapping


def test_init_callback_sets_core_and_returns_requested_step_indices(mock_core: MagicMock) -> None:
    """`init_callback` should initialize the core and honor an explicit `call_every_nth_mj_step`."""
    mock_core.mj_step_index_final = 10
    callback = EarlyTerminationIfAnyBoxTouchesFloorCallback(body_name_to_size_mapping={}, call_every_nth_mj_step=4)

    relevant_indices = callback.init_callback(mock_core)

    assert relevant_indices == [0, 4, 8, 12]
    assert callback.core is mock_core


@pytest.mark.parametrize(
    ("z_center_of_mass", "half_extent_z", "expected_terminate"),
    [
        (0.5, 0.4, False),
        (-0.5, 0.1, True),
        (0.05, 0.2, True),
    ],
    ids=["safely_on_carrier", "center_of_mass_below_carrier_top", "bottom_side_below_floor_contact"],
)
def test_call_detects_dropped_box(
    mock_core: MagicMock, z_center_of_mass: float, half_extent_z: float, expected_terminate: bool
) -> None:
    """`call` should terminate whenever a box's center of mass or bottom side falls below the carrier."""
    body_id = mock_core.model.body("box_a").id
    mock_core.data.xpos[body_id] = [0.0, 0.0, z_center_of_mass]
    mock_core.data.xquat[body_id] = [1.0, 0.0, 0.0, 0.0]
    callback = EarlyTerminationIfAnyBoxTouchesFloorCallback(
        body_name_to_size_mapping={"box_a": (0.2, 0.2, half_extent_z)}
    )
    callback._core = mock_core

    assert callback.call() is expected_terminate


def test_call_stops_checking_further_bodies_once_a_dropped_box_is_found(mock_core: MagicMock) -> None:
    """`call` should short-circuit and not evaluate remaining bodies once a dropped box has been found."""
    body_id = mock_core.model.body("box_a").id
    mock_core.data.xpos[body_id] = [0.0, 0.0, -0.5]
    mock_core.data.xquat[body_id] = [1.0, 0.0, 0.0, 0.0]
    callback = EarlyTerminationIfAnyBoxTouchesFloorCallback(
        body_name_to_size_mapping={"box_a": (0.1, 0.1, 0.1), "nonexistent_body": (0.1, 0.1, 0.1)}
    )
    callback._core = mock_core

    assert callback.call() is True


def test_reset_and_post_run_are_no_ops(mock_core: MagicMock) -> None:
    """`reset` and `post_run` should not raise and should not alter the configured mapping."""
    mapping = {"box_a": (0.1, 0.1, 0.1)}
    callback = EarlyTerminationIfAnyBoxTouchesFloorCallback(body_name_to_size_mapping=mapping)
    callback._core = mock_core

    callback.reset()
    callback.post_run()

    assert callback.body_name_to_size_mapping == mapping
