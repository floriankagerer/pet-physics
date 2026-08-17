"""Contains callback related utility functions."""

from pet_physics.simulation.callbacks.base_callback import BaseCallback
from pet_physics.simulation.callbacks.recorder_callback import RecorderCallback
from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities


def is_callback_instance_in_list(callback_list: list[BaseCallback] | None, callback_class: type) -> bool:
    """Checks whether an instance of the given callback class is contained in the given callback list.

    Args:
        callback_list: The list of callbacks to check.
        callback_class: The callback class to check for.

    Returns:
        `True` if an instance of the given callback class is contained in the given callback list, `False` otherwise.
    """
    if callback_list is None:
        return False

    for callback in callback_list:
        if isinstance(callback, callback_class):
            return True

    return False


def get_collection_body_quantities_from_callbacks(
    core_callbacks: list[RecorderCallback | BaseCallback],
) -> CollectionBodyQuantities | None:
    """Extracts the `CollectionBodyQuantities` from the given list of core callbacks.

    Args:
        core_callbacks: The list of core callbacks.

    Returns:
        The extracted collection of body quantities. If no `RecorderCallback` is found in the given callbacks,
            `None` is returned.
    """
    for callback in core_callbacks:
        if isinstance(callback, RecorderCallback):
            return callback.collection_body_quantities

    return None
