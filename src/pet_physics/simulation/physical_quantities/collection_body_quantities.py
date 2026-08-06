"""This module is responsible for gathering all quantities that are body specific, e.g., force or penetration."""

import structlog

from pet_physics.simulation.physical_quantities.history.base_history import BaseHistory
from pet_physics.simulation.physical_quantities.quantity_names import QuantityName

logger = structlog.get_logger(__name__)


class CollectionBodyQuantities:
    """This class gathers all body related quantities, e.g., force."""

    def __init__(self) -> None:
        """The constructor."""

        self._quantity_histories: dict[QuantityName, BaseHistory] = {}
        """A dictionary that contains the quantity histories for every body related quantity."""

    @property
    def registered_quantities(self) -> list[QuantityName]:
        """The quantity names of all registered body related quantities."""
        return list(self._quantity_histories.keys())

    def unregister_quantity_history(self, quantity_history_name: QuantityName) -> None:
        """Unregisters the quantity history for the requested quantity name.

        Args:
            quantity_history_name: The name of the quantity whose history is to be unregistered.
        """
        if quantity_history_name not in self._quantity_histories:
            raise ValueError(f"No history with the name '{quantity_history_name}' is registered.")

        del self._quantity_histories[quantity_history_name]

    def register_quantity_history(self, quantity_history_name: QuantityName, history: BaseHistory) -> None:
        """Registers the quantity history for the requested quantity name.

        Args:
            quantity_history_name: The name of the quantity whose history is to be registered.
            history: The history object to be registered.
        """

        if quantity_history_name in self._quantity_histories:
            raise ValueError(f"A history with the name '{quantity_history_name}' is already registered.")

        self._quantity_histories[quantity_history_name] = history

    def get_quantity_history(self, quantity_history_name: QuantityName) -> BaseHistory:
        """Gets the quantity history for the requested quantity name.

        Args:
            quantity_history_name: The name of the quantity whose history is requested.
        """
        history = self._quantity_histories.get(quantity_history_name)

        if history is None:
            raise ValueError(f"No history with the name '{quantity_history_name}' is registered.")

        return history
