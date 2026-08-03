"""Tests for `simulation.callbacks.callback_orchestrator`."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from pet_physics.simulation.callbacks import callback_orchestrator
from pet_physics.simulation.callbacks.base_callback import BaseCallback
from pet_physics.simulation.callbacks.callback_orchestrator import CallbackOrchestrator

if TYPE_CHECKING:
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore


class _RecordingCallback(BaseCallback):
    """A `BaseCallback` double that records invocations of its lifecycle methods."""

    def __init__(
        self,
        mj_steps: list[int] | None = None,
        call_result: bool = False,
        init_order: list[str] | None = None,
        name: str = "callback",
    ) -> None:
        super().__init__()
        self._mj_steps = mj_steps
        self.call_result = call_result
        self._init_order = init_order
        self.name = name
        self.call_count = 0
        self.reset_count = 0
        self.post_run_count = 0

    def init_callback(self, core: PETPhysicsCore) -> list[int] | None:
        """Sets the core and records the invocation, then reports the configured relevant steps."""
        self._core = core
        if self._init_order is not None:
            self._init_order.append(self.name)
        return self._mj_steps

    def call(self) -> bool:
        """Records the invocation and returns the configured call result."""
        self.call_count += 1
        return self.call_result

    def post_run(self) -> None:
        """Records the invocation."""
        self.post_run_count += 1

    def reset(self) -> None:
        """Records the invocation."""
        self.reset_count += 1


def test_initialize_calls_callbacks_in_type_sorted_order(monkeypatch: pytest.MonkeyPatch, mock_core: MagicMock) -> None:
    """Should initialize callbacks in the order defined by `CALLBACK_TYPE_SORTING_KEY_MAPPING`."""

    class _First(_RecordingCallback):
        """A recording callback assigned the first sorting key."""

    class _Second(_RecordingCallback):
        """A recording callback assigned the second sorting key."""

    class _Third(_RecordingCallback):
        """A recording callback assigned the third sorting key."""

    monkeypatch.setattr(callback_orchestrator, "CALLBACK_TYPE_SORTING_KEY_MAPPING", {_First: 0, _Second: 1, _Third: 2})

    init_order: list[str] = []
    third = _Third(init_order=init_order, name="third")
    first = _First(init_order=init_order, name="first")
    second = _Second(init_order=init_order, name="second")

    orchestrator = CallbackOrchestrator([third, first, second])
    orchestrator.initialize(mock_core)

    assert init_order == ["first", "second", "third"]


def test_initialize_calls_unmapped_type_callback_after_mapped_ones(
    monkeypatch: pytest.MonkeyPatch, mock_core: MagicMock
) -> None:
    """Should initialize a callback whose type is absent from the mapping after all mapped-type callbacks."""

    class _Mapped(_RecordingCallback):
        """A recording callback whose type is present in the sorting mapping."""

    class _Unmapped(_RecordingCallback):
        """A recording callback whose type is absent from the sorting mapping."""

    monkeypatch.setattr(callback_orchestrator, "CALLBACK_TYPE_SORTING_KEY_MAPPING", {_Mapped: 0})

    init_order: list[str] = []
    unmapped = _Unmapped(init_order=init_order, name="unmapped")
    mapped = _Mapped(init_order=init_order, name="mapped")

    orchestrator = CallbackOrchestrator([unmapped, mapped])
    orchestrator.initialize(mock_core)

    assert init_order == ["mapped", "unmapped"]


def test_initialize_passes_core_to_every_callback(mock_core: MagicMock) -> None:
    """Should pass the given core to `init_callback` of every registered callback."""
    first = _RecordingCallback(name="first")
    second = _RecordingCallback(name="second")

    orchestrator = CallbackOrchestrator([first, second])
    orchestrator.initialize(mock_core)

    assert first.core is mock_core
    assert second.core is mock_core


def test_initialize_excludes_callback_without_relevant_steps_from_schedule(mock_core: MagicMock) -> None:
    """Should not schedule a callback whose `init_callback` reports no relevant simulation steps."""
    mock_core.n_mj_steps = 0
    unscheduled = _RecordingCallback(mj_steps=None)

    orchestrator = CallbackOrchestrator([unscheduled])
    orchestrator.initialize(mock_core)
    orchestrator.call()

    assert unscheduled.call_count == 0


def test_call_invokes_only_callbacks_scheduled_for_current_step(mock_core: MagicMock) -> None:
    """Should call only the callbacks whose relevant steps include the current `n_mj_steps`."""
    mock_core.n_mj_steps = 10
    due = _RecordingCallback(mj_steps=[10])
    not_due = _RecordingCallback(mj_steps=[20])

    orchestrator = CallbackOrchestrator([due, not_due])
    orchestrator.initialize(mock_core)
    orchestrator.call()

    assert due.call_count == 1
    assert not_due.call_count == 0


def test_call_returns_false_when_no_callback_scheduled_for_current_step(mock_core: MagicMock) -> None:
    """Should return `False` when no callback is scheduled for the current simulation step."""
    mock_core.n_mj_steps = 99
    callback = _RecordingCallback(mj_steps=[10])

    orchestrator = CallbackOrchestrator([callback])
    orchestrator.initialize(mock_core)

    assert orchestrator.call() is False


def test_call_returns_true_if_any_scheduled_callback_terminates_simulation(mock_core: MagicMock) -> None:
    """Should return `True` if at least one scheduled callback signals the end of the simulation."""
    mock_core.n_mj_steps = 5
    continuing = _RecordingCallback(mj_steps=[5], call_result=False)
    terminating = _RecordingCallback(mj_steps=[5], call_result=True)

    orchestrator = CallbackOrchestrator([continuing, terminating])
    orchestrator.initialize(mock_core)

    assert orchestrator.call() is True


def test_call_raises_runtime_error_when_orchestrator_has_no_callbacks(mock_core: MagicMock) -> None:
    """Should raise a `RuntimeError` when calling without any registered callback."""
    orchestrator = CallbackOrchestrator([])
    orchestrator.initialize(mock_core)

    with pytest.raises(RuntimeError):
        orchestrator.call()


def test_reset_calls_reset_on_every_callback() -> None:
    """Should call `reset` on every registered callback."""
    first = _RecordingCallback()
    second = _RecordingCallback()

    orchestrator = CallbackOrchestrator([first, second])
    orchestrator.reset()

    assert first.reset_count == 1
    assert second.reset_count == 1


def test_post_run_calls_post_run_on_every_callback() -> None:
    """Should call `post_run` on every registered callback."""
    first = _RecordingCallback()
    second = _RecordingCallback()

    orchestrator = CallbackOrchestrator([first, second])
    orchestrator.post_run()

    assert first.post_run_count == 1
    assert second.post_run_count == 1
