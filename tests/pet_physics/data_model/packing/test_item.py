"""Tests the module `item`."""

from pet_physics.data_model.packing.item import Item


def test_item_serialization() -> None:
    """Tests whether an object of the dataclass `Item` is correctly serialized."""
    item = Item(
        id="id_test",
        article="article_test",
        product_group="product_group_test",
        length_mm=300,
        width_mm=200,
        height_mm=100,
        weight_kg=3.14,
        sequence=1,
    )

    serialized_item = {
        "id": "id_test",
        "article": "article_test",
        "product_group": "product_group_test",
        "length_mm": 300,
        "width_mm": 200,
        "height_mm": 100,
        "weight_kg": 3.14,
        "sequence": 1,
    }

    assert item.to_dict() == serialized_item


def test_item_deserialization() -> None:
    """Tests whether we correctly deserialize."""
    serialized_item = {
        "article": "article",
        "id": "id",
        "product_group": "pg",
        "length_mm": 300,
        "width_mm": 200,
        "height_mm": 100,
        "weight_kg": 3.14,
        "sequence": 1,
    }

    expected_item = Item(
        article="article",
        id="id",
        product_group="pg",
        length_mm=300,
        width_mm=200,
        height_mm=100,
        weight_kg=3.14,
        sequence=1,
    )

    deserialized = Item.from_dict(serialized_item)

    assert deserialized == expected_item


def test_item_color_identifier() -> None:
    """Tests whether the correct attribute/value for the color identifier is returned."""
    item = Item(
        id="id_test",
        article="article_test",
        product_group="product_group_test",
        length_mm=300,
        width_mm=200,
        height_mm=100,
        weight_kg=3.14,
        sequence=1,
    )

    assert item.color_identifier == "article_test"
