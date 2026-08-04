"""Data model for defining stability checks used in simulation evaluation."""

from dataclasses import dataclass, field
from typing import Literal

from dataclasses_json import dataclass_json

from pet_physics.data_model.evaluation.stability_check_configuration import StabilityCheckConfiguration


@dataclass_json
@dataclass
class StabilityCheck:
    """Defines a stability check type and its configuration for evaluating a simulation.

    Attributes:
        check_type: The type of stability check to perform. It can be one of the following:
            - `"one_by_one"`: Teleports the bodies one by one.
            - `"static"`: Places all bodies at once according to the packing plan.
            - `"wiggle"`: Similar to static but with additional forces that act on the bin to check how the stability
                of a pallet behaves if the pallet is moved.
        check_configuration: Optional configuration for the stability check. This can contain, e.g., a *size reduction*
            of the boxes, or a definition of the wiggeling.
    """

    check_type: Literal["one_by_one", "static", "wiggle"] = "one_by_one"
    check_configuration: StabilityCheckConfiguration | None = field(default_factory=StabilityCheckConfiguration)

    @property
    def is_type_one_by_one(self) -> bool:
        """Indicates whether the `check_type` equals `"one_by_one"`."""
        return self.check_type == "one_by_one"

    @property
    def is_type_static(self) -> bool:
        """Indicates whether the `check_type` equals `"static"`."""
        return self.check_type == "static"

    @property
    def is_type_wiggle(self) -> bool:
        """Indicates whether the `check_type` equals `"wiggle"`."""
        return self.check_type == "wiggle"
