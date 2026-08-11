"""This module creates a callback for a given (quantity) recorder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pet_physics.data_model.physical_quantities.simulation_time import SimulationTime
from pet_physics.simulation.callbacks.base_callback import BaseCallback
from pet_physics.simulation.mujoco_lookup_helpers import get_body_names_in_model
from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities
from pet_physics.simulation.physical_quantities.recorders.base_recorder import BaseRecorder

if TYPE_CHECKING:
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore


class RecorderCallback(BaseCallback):
    """This class works as wrapper that creates a recorder callback for a given recorder class."""

    def __init__(
        self, recorder_class: type[BaseRecorder], collection_body_quantities: CollectionBodyQuantities
    ) -> None:
        """Constructor of the recorder to callback wrapper.

        Args:
            recorder_class: The type of the recorder class that is set for the quantity recording.
            collection_body_quantities: The collection of all body quantities that were recorded during the simulation.
        """
        super().__init__()

        self._recorder_class = recorder_class
        """The class of the recorder."""

        self._collection_body_quantities = collection_body_quantities
        """The collection of all body quantities that were recorded during the simulation."""

        self._recorder: BaseRecorder
        """The recorder that records the quantities during the simulation. Note that this attribute is initialized in
        `self.init_callback` and `self.reset`, respectively, later."""
        self._i: int
        """A counter that points to the i-th entry of the simulation quantities. Note that this attribute is initialized
        in `self.init_callback` and `self.reset`, respectively, later."""
        self._n_planned_calls: int | None = None
        """The number of times this callback is called during the simulation. This defines the length of a recorder's
        quantity history. Note that this attribute is initialized in `self.init_callback`"""

    @property
    def collection_body_quantities(self) -> CollectionBodyQuantities:
        """The collection of all body quantities that were recorded during the simulation."""
        return self._collection_body_quantities

    @property
    def simulation_time(self) -> SimulationTime:
        """The recorded simulation time in each simulation step."""
        return self._recorder.sim_time

    @property
    def n_planned_calls(self) -> int:
        """The number of times this callback is called during the simulation. This defines the length of a recorder's
        quantity history."""
        if self._n_planned_calls is None:
            msg = (
                "The number of planned calls has not been initialized in callback yet. "
                f"Please call '{self.init_callback.__name__}' first."
            )
            raise RuntimeError(msg)

        return self._n_planned_calls

    def init_callback(self, core: PETPhysicsCore) -> list[int]:
        """Initializes the callback, e.g., by setting the simulation core and preparing any necessary data.

        In general, this method is called **before** the first `core.step` call.

        Args:
            core: The core this callback is added to.

        Returns:
            The list of `mujoco.mj_step` call indices at that this callback is called.
        """
        self._core = core

        relevant_mj_step_indices = self.call_on_every_nth_mj_step()
        self._n_planned_calls = len(relevant_mj_step_indices)

        self.reset()

        return relevant_mj_step_indices

    def call(self) -> bool:
        """This method is called after each `core.step`. The return value indicates whether the simulation finishes."""

        self._recorder.record(self._i, self.core.model, self.core.data)
        self._i += 1

        return False

    def post_run(self) -> None:
        """This method is called **after** a `core.run` has completed."""
        # nothing to do after run
        pass

    def reset(self) -> None:
        """This method resets the object such that it is in its initial state."""

        self._recorder = self._recorder_class(
            mj_model=self.core.model,
            bodies=get_body_names_in_model(self.core.model),
            n_steps=self.n_planned_calls,
        )

        for quantity_history_name, history in self._recorder.get_quantity_history_registrations():
            if quantity_history_name in self._collection_body_quantities.registered_quantities:
                self._collection_body_quantities.unregister_quantity_history(quantity_history_name)

            self._collection_body_quantities.register_quantity_history(quantity_history_name, history)

        self._i = 0
