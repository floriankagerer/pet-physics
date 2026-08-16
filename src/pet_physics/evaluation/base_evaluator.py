"""Base class and metaclass for all simulation evaluators."""

from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod

_REQUIRED_CLASS_VARIABLE_NAME = "cl_name"
"""Defines the name of the class variable every evaluator must have."""


class AbstractClassVariableMeta(ABCMeta):
    """Metaclass that enforces required class variable declarations on evaluator subclasses."""

    def __new__(mcs, name, bases, namespace):
        """Creates a new class, enforcing that concrete subclasses define `cl_name`.

        Args:
            name (str): The name of the class being created.
            bases (tuple): The base classes of the class being created.
            namespace (dict): The class namespace dictionary.

        Returns:
            type: The newly created class.

        Raises:
            NotImplementedError: If a concrete subclass does not define `cl_name`.
        """
        cls = super().__new__(mcs, name, bases, namespace)

        # Skip checking the abstract base class itself
        if name == "BaseEvaluator":
            return cls

        # Check if we're dealing with a concrete class (not another ABC)
        if ABC not in bases and any(issubclass(base, BaseEvaluator) for base in bases):
            # Verify that class_variable is defined in this class
            if not hasattr(cls, _REQUIRED_CLASS_VARIABLE_NAME):
                msg = f"class '{name}' must define '{_REQUIRED_CLASS_VARIABLE_NAME}'"
                raise NotImplementedError(msg)

        return cls


class BaseEvaluator(ABC, metaclass=AbstractClassVariableMeta):
    """Base class for all evaluators.

    Attributes:
        cl_name: The name of this evaluator. This class variable must be defined in all subclasses.
    """

    cl_name: str

    @abstractmethod
    def evaluate(self, *args, **kwargs):
        """Evaluates the simulation run and returns the result.

        Args:
            *args: Positional arguments specific to each evaluator implementation.
            **kwargs: Keyword arguments specific to each evaluator implementation.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclass must implement evaluate()")
