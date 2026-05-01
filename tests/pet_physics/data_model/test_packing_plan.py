"""Tests the `packing_plan` module."""

from pet_physics.data_model.action import Action
from pet_physics.data_model.item import Item
from pet_physics.data_model.orientation import Orientation
from pet_physics.data_model.packing_plan import PackingPlan
from pet_physics.data_model.position_3d import Position3D


def test_packing_plan_serialization() -> None:
    """Tests whether an object of the dataclass `Action` is correctly serialized."""

    actual_packing_plan = PackingPlan(
        id="packing_plan_id",
        actions=[
            Action(
                item=Item(
                    id="id",
                    article="article",
                    product_group="product_group",
                    length_mm=300,
                    width_mm=200,
                    height_mm=100,
                    weight_kg=3.14,
                    sequence=1,
                ),
                orientation=Orientation.LWH,
                flb_coordinates=Position3D(x=200, y=100, z=0, area=None),
            )
        ],
    )

    expected_serialized = {
        "id": "packing_plan_id",
        "actions": [
            {
                "item": {
                    "id": "id",
                    "article": "article",
                    "product_group": "product_group",
                    "length_mm": 300,
                    "width_mm": 200,
                    "height_mm": 100,
                    "weight_kg": 3.14,
                    "sequence": 1,
                },
                "orientation": 0,
                "flb_coordinates": [200, 100, 0],
            }
        ],
    }

    assert actual_packing_plan.to_dict() == expected_serialized


def test_packing_deserialization() -> None:
    """Tests whether we correctly deserialize."""
    serialized_packing_plan = {
        "id": "packing_plan_id",
        "actions": [
            {
                "item": {
                    "id": "id",
                    "article": "article",
                    "product_group": "product_group",
                    "length_mm": 300,
                    "width_mm": 200,
                    "height_mm": 100,
                    "weight_kg": 3.14,
                    "sequence": 1,
                },
                "orientation": 0,
                "flb_coordinates": [200, 100, 0],
            }
        ],
    }

    expected_packing_plan = PackingPlan(
        id="packing_plan_id",
        actions=[
            Action(
                item=Item(
                    id="id",
                    article="article",
                    product_group="product_group",
                    length_mm=300,
                    width_mm=200,
                    height_mm=100,
                    weight_kg=3.14,
                    sequence=1,
                ),
                orientation=Orientation.LWH,
                flb_coordinates=Position3D(x=200, y=100, z=0, area=None),
            )
        ],
    )

    deserialized = PackingPlan.from_dict(serialized_packing_plan)

    assert deserialized == expected_packing_plan
