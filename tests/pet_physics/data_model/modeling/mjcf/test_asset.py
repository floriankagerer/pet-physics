"""Tests for the asset module."""

from pet_physics.data_model.modeling.mjcf.asset import Asset


def test_asset_to_xml_string():
    asset = Asset()
    assert asset.to_xml_string() == "<asset />"
