"""Configuration data model for stability checks."""

from dataclasses import dataclass, field
from typing import Literal, Self, get_args

import structlog
from dataclasses_json import dataclass_json

logger = structlog.get_logger(__name__)
"""The logger of this module."""

RecognizedParametersType = Literal["total_simulation_time_seconds", "box_size_reduction_absolute_mm"]
"""The literal that define the recognized parameters."""
RECOGNIZED_PARAMETERS = get_args(RecognizedParametersType)
"""The recognized parameter keys that are derived from the `Literal` definition."""


@dataclass_json
@dataclass
class StabilityCheckConfiguration:
    """The configuration of a stability check.

    Attributes:
        parameters: The parameters for the additional configuration of a stability check. This can contain, e.g., a
            *size reduction* of the boxes, or a definition of the wiggeling.
    """

    parameters: dict[RecognizedParametersType, str | int | float] = field(default_factory=dict)

    def __post_init__(self):
        all_keys = list(self.parameters.keys())

        for key in all_keys:
            if key not in RECOGNIZED_PARAMETERS:
                msg = f"parameter '{key}' is not recognized - ignoring"
                logger.warning(msg)
                self.parameters.pop(key, None)

    def add_parameter(self, key: RecognizedParametersType, value: str | int | float) -> Self:
        """Adds a key-value parameter pair to the configuration.

        Args:
            key: The parameter key to add.
            value: The value for the parameter.

        Returns:
            This instance with the parameter added.
        """
        if key not in RECOGNIZED_PARAMETERS:
            msg = f"parameter '{key}' is not recognized - ignoring"
            logger.warning(msg)
        else:
            if key in self.parameters:
                logger.warning(f"configuration '{key}' will be overwritten")
            self.parameters[key] = value

        return self

    @property
    def total_simulation_time_seconds(self) -> float | int | None:
        """The total simulation duration in seconds. If this parameter is unset, `None` is returned."""
        return self.parameters.get("total_simulation_time_seconds", None)

    @property
    def box_size_reduction_absolute_mm(self) -> float | int:
        """The absolute box size reduction in mm. Returns 0 if not set."""
        return self.parameters.get("box_size_reduction_absolute_mm", 0)
