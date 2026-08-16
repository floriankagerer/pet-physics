"""Contains a class that represents a collection of packing plans."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pet_physics.data_model.packing.action import Action
from pet_physics.data_model.packing.packing_plan import PackingPlan


@dataclass
class CollectionPackingPlan:
    """A collection of packing plans, e.g., all carriers produced by a single packing run.

    Attributes:
        packing_plans: The packing plans contained in this collection.
    """

    packing_plans: list[PackingPlan]

    @classmethod
    def from_file(cls, file_path: Path) -> Self:
        """Builds a `CollectionPackingPlan` from a packing plan JSON file.

        The file maps each bin id directly to the ordered list of its packed items, rather than nesting them
        under an `"actions"` key as `PackingPlan.from_dict` expects.

        Args:
            file_path: The path of the JSON file to read.

        Returns:
            The parsed collection of packing plans, one per bin id.
        """
        with open(file_path) as file:
            raw_packing_plans: dict[str, list[dict]] = json.load(file)

        packing_plans = [
            PackingPlan(
                id=bin_id,
                actions=[Action.from_dict(serialized_action) for serialized_action in serialized_actions],
            )
            for bin_id, serialized_actions in raw_packing_plans.items()
        ]

        return cls(packing_plans=packing_plans)
