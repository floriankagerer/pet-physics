"""Tests for `simulation.callbacks.call_schedule`."""

from unittest.mock import MagicMock

from pet_physics.simulation.callbacks.base_callback import BaseCallback
from pet_physics.simulation.callbacks.call_schedule import CallSchedule


def _mock_callback() -> MagicMock:
    """Creates a mock callback conforming to `BaseCallback`."""
    return MagicMock(spec=BaseCallback)


def test_from_callbacks_with_mj_steps_returns_empty_schedule_for_no_callbacks() -> None:
    """Should return an empty schedule when no callbacks are given."""
    schedule = CallSchedule.from_callbacks_with_mj_steps([])

    assert schedule.items == {}


def test_from_callbacks_with_mj_steps_ignores_callback_without_steps() -> None:
    """Should not add a schedule entry for a callback that has no relevant steps."""
    callback = _mock_callback()

    schedule = CallSchedule.from_callbacks_with_mj_steps([(callback, [])])

    assert schedule.items == {}


def test_from_callbacks_with_mj_steps_maps_single_callback_to_single_step() -> None:
    """Should map a callback to its single relevant simulation step."""
    callback = _mock_callback()

    schedule = CallSchedule.from_callbacks_with_mj_steps([(callback, [10])])

    assert schedule.items == {10: [callback]}


def test_from_callbacks_with_mj_steps_maps_single_callback_to_multiple_steps() -> None:
    """Should map a callback to every one of its relevant simulation steps."""
    callback = _mock_callback()

    schedule = CallSchedule.from_callbacks_with_mj_steps([(callback, [0, 10, 20])])

    assert schedule.items == {0: [callback], 10: [callback], 20: [callback]}


def test_from_callbacks_with_mj_steps_groups_multiple_callbacks_at_shared_step() -> None:
    """Should list all callbacks sharing a simulation step together, preserving input order."""
    first_callback = _mock_callback()
    second_callback = _mock_callback()

    schedule = CallSchedule.from_callbacks_with_mj_steps([(first_callback, [5]), (second_callback, [5])])

    assert schedule.items == {5: [first_callback, second_callback]}


def test_from_callbacks_with_mj_steps_keeps_callbacks_at_distinct_steps_separate() -> None:
    """Should keep callbacks with non-overlapping relevant steps in separate schedule entries."""
    first_callback = _mock_callback()
    second_callback = _mock_callback()

    schedule = CallSchedule.from_callbacks_with_mj_steps([(first_callback, [5]), (second_callback, [15])])

    assert schedule.items == {5: [first_callback], 15: [second_callback]}
