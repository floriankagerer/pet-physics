import pytest

from pet_physics.data_model.modeling.mjcf.material import Material


@pytest.mark.parametrize(
    "material, expected_xml_string",
    [
        (
            Material(name="grid", texture="grid", texrepeat=(2, 2), texuniform="true", reflectance=0.0),
            '<material name="grid" texture="grid" texrepeat="2 2" texuniform="true" reflectance="0.0" />',
        ),
        (Material(name="arrow.x", rgba=(1, 0, 0, 1)), '<material name="arrow.x" rgba="1 0 0 1" />'),
    ],
)
def test_material_to_xml_string(material: Material, expected_xml_string: str) -> None:
    assert material.to_xml_string() == expected_xml_string
