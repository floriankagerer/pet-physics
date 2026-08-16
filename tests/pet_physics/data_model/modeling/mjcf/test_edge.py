"""This module tests the data model of a `Edge` object."""

from pet_physics.data_model.modeling.mjcf.edge import Edge


def test_edge_to_xml_string():
    """Tests the constructor of the dataclass `Edge`."""
    edge = Edge(equality="true")
    expected_xml_string = """<edge equality="true" />"""

    assert edge.to_xml_string() == expected_xml_string
