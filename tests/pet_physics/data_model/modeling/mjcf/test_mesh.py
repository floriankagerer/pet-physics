"""Tests the mesh module."""

from pet_physics.data_model.modeling.mjcf.mesh import Mesh


def test_mesh_to_xml_string():
    """Tests whether a `Mesh` instance is correctly converted."""
    mesh = Mesh(name="test", file="path/to/mesh.obj", scale=(0.5, 0.5, 0.5))
    expected_xml_string = '<mesh name="test" file="path/to/mesh.obj" scale="0.5 0.5 0.5" />'

    assert mesh.to_xml_string() == expected_xml_string
