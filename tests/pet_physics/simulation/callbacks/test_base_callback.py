"""Tests for `BaseCallback`."""

from unittest.mock import MagicMock

import mujoco
import pytest

from pet_physics.simulation.callbacks.base_callback import BaseCallback


class _DummyCallback(BaseCallback):
    """A minimal concrete `BaseCallback` used to exercise the base class in isolation."""

    def init_callback(self, core) -> list[int]:
        """Sets the core without any further initialization."""
        self._core = core
        return []

    def call(self) -> bool:
        """Always reports that the simulation should continue."""
        return False

    def post_run(self) -> None:
        """No-op post-run hook."""
        pass

    def reset(self) -> None:
        """No-op reset."""
        pass


@pytest.fixture
def callback() -> _DummyCallback:
    """A fresh, uninitialized dummy callback."""
    return _DummyCallback()


def test_core_property_raises_before_initialization(callback: _DummyCallback) -> None:
    """Accessing `core` before `init_callback` has been called should raise a `RuntimeError`."""
    with pytest.raises(RuntimeError):
        _ = callback.core


def test_core_property_returns_core_after_initialization(callback: _DummyCallback, mock_core: MagicMock) -> None:
    """Accessing `core` after `init_callback` should return the initialized core."""
    callback.init_callback(mock_core)

    assert callback.core is mock_core


def test_get_body_id_delegates_to_model_lookup(
    callback: _DummyCallback, mock_core: MagicMock, mj_model: mujoco.MjModel
) -> None:
    """`get_body_id` should return the id of the body with the given name in the core's model."""
    callback.init_callback(mock_core)

    body_id = callback.get_body_id("box_a")

    assert body_id == mujoco.mj_name2id(mj_model, mujoco.mjtObj.mjOBJ_BODY, "box_a")


@pytest.mark.parametrize(
    ("simulation_time", "expected_index"),
    [(0.0, 0), (0.25, 2), (0.29, 2)],
)
def test_convert_simulation_time_to_mj_step_index(
    callback: _DummyCallback, simulation_time: float, expected_index: int
) -> None:
    """Should floor-divide the simulation time by the model timestep."""
    callback.init_callback(MagicMock(mj_model_timestep=0.1))

    assert callback.convert_simulation_time_to_mj_step_index(simulation_time) == expected_index


def test_convert_simulation_times_to_mj_step_indices_maps_each_time(callback: _DummyCallback) -> None:
    """Should apply the single-time conversion to every entry of the input list."""
    callback.init_callback(MagicMock(mj_model_timestep=0.1))

    indices = callback.convert_simulation_times_to_mj_step_indices([0.0, 0.25, 0.5])

    assert indices == [0, 2, 5]


def test_call_on_every_nth_mj_step_with_explicit_n(callback: _DummyCallback) -> None:
    """With an explicit `n`, the returned indices should be every n-th index up to the final step."""
    callback.init_callback(MagicMock(mj_step_index_final=10))

    assert callback.call_on_every_nth_mj_step(n=3) == [0, 3, 6, 9]


def test_call_on_every_nth_mj_step_defaults_to_core_run_timestep_ratio(callback: _DummyCallback) -> None:
    """Without an explicit `n`, the core's `mj_steps_per_core_run_timestep` should be used."""
    callback.init_callback(MagicMock(mj_step_index_final=10, mj_steps_per_core_run_timestep=5))

    assert callback.call_on_every_nth_mj_step() == [0, 5, 10]
