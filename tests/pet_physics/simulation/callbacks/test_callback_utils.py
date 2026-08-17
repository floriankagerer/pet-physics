"""Tests for `simulation.callbacks.utils`."""

from unittest.mock import MagicMock

from pet_physics.simulation.callbacks.callback_utils import (
    get_collection_body_quantities_from_callbacks,
    is_callback_instance_in_list,
)
from pet_physics.simulation.callbacks.recorder_callback import RecorderCallback


class _Foo:
    """A dummy marker class used to test `is_callback_instance_in_list`."""


class _Bar:
    """A second, unrelated dummy marker class used to test `is_callback_instance_in_list`."""


def test_is_callback_instance_in_list_returns_false_for_none() -> None:
    """Should return `False` when the callback list is `None`."""
    assert is_callback_instance_in_list(None, _Foo) is False


def test_is_callback_instance_in_list_returns_false_for_empty_list() -> None:
    """Should return `False` when the callback list is empty."""
    assert is_callback_instance_in_list([], _Foo) is False


def test_is_callback_instance_in_list_returns_true_when_instance_present() -> None:
    """Should return `True` when an instance of the given class is present in the list."""
    assert is_callback_instance_in_list([_Bar(), _Foo()], _Foo) is True


def test_is_callback_instance_in_list_returns_false_when_instance_absent() -> None:
    """Should return `False` when no instance of the given class is present in the list."""
    assert is_callback_instance_in_list([_Bar()], _Foo) is False


def test_get_collection_body_quantities_from_callbacks_returns_none_without_recorder_callback() -> None:
    """Should return `None` when no `RecorderCallback` is present in the list."""
    assert get_collection_body_quantities_from_callbacks([MagicMock()]) is None


def test_get_collection_body_quantities_from_callbacks_returns_quantities_of_recorder_callback() -> None:
    """Should return the `collection_body_quantities` of the `RecorderCallback` found in the list."""
    recorder_callback = MagicMock(spec=RecorderCallback)
    recorder_callback.collection_body_quantities = "sentinel-quantities"

    result = get_collection_body_quantities_from_callbacks([MagicMock(), recorder_callback])

    assert result == "sentinel-quantities"
