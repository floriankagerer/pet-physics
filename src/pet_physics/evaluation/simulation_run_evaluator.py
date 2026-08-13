"""Manager for evaluators applied to a complete simulation run."""

from typing import Any

import structlog

from pet_physics.evaluation.base_evaluator import BaseEvaluator

logger = structlog.get_logger(__name__)


class SimulationRunEvaluator:
    """Manages and runs all evaluators registered for a simulation run."""

    def __init__(self) -> None:
        self._evaluators: dict[str, BaseEvaluator] = {}
        """The registered evaluators that are used for evaluating a simulation run."""

    def register_evaluator(self, evaluator: BaseEvaluator) -> None:
        """Registers the given evaluator and stores the name.

        Args:
            evaluator: The evaluator you want to register.
        """
        name = evaluator.cl_name
        if name in self._evaluators:
            logger.warning(f"evaluator '{name}' is already defined - overwrite previous definition")
        self._evaluators[name] = evaluator

    def eval(self, evaluator_name: str, *args, **kwargs) -> Any:
        """Runs a specific evaluator by name, skipping it with a warning if not registered.

        Args:
            evaluator_name: The name of the evaluator to run.
            *args: Positional arguments forwarded to the evaluator.
            **kwargs: Keyword arguments forwarded to the evaluator.

        Returns:
            The result returned by the evaluator, or `None` if not registered.
        """

        if evaluator_name not in self._evaluators:
            logger.warning(f"evaluator '{evaluator_name}' not registered - skipping")
        else:
            return self._evaluators[evaluator_name].evaluate(*args, **kwargs)
