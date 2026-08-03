"""This module contains callbacks for the core of the MuJoCo simulation."""

from pet_physics.simulation.callbacks.base_callback import BaseCallback

# TODO(florian): If we consider performance issues, we might want to refactor this logic and use `Iterator` instead of
#             `list` in some places. This requires changes in multiple places.
CallbackWithMjSteps = tuple[BaseCallback, list[int]]
"""A type alias for a tuple of callback and its relevant simulation steps."""
