"""Tests the module `mjcf_utils`."""

from pathlib import Path

import mujoco
import pytest

from pet_physics.utils.mjcf_utils import (
    DEFAULT_WEIGHT_G,
    MJCFUtils,
    bankers_rounding,
    custom_name_encode,
    get_body_and_geom_name,
    round_half_up,
)

_MINIMAL_MODEL_XML = """
<mujoco model="mjcf_utils_test_model">
  <worldbody>
    <body name="box" pos="0 0 0.5">
      <geom name="box_geom" type="box" size="0.1 0.1 0.1" mass="1" />
    </body>
  </worldbody>
</mujoco>
"""


@pytest.fixture
def mj_model() -> mujoco.MjModel:
    """A minimal MuJoCo model used to test MJCF file export."""
    return mujoco.MjModel.from_xml_string(_MINIMAL_MODEL_XML)


@pytest.mark.parametrize(
    "body_name, expected_output",
    [
        ("plain_name", "plain_name"),
        ("name#1", "name\\#1"),
        ("name&co", "nameANDco"),
        ('name"quoted"', "name\\u0022quoted\\u0022"),
        ('a#b&c"d', "a\\#bANDc\\u0022d"),
    ],
)
def test_custom_name_encode(body_name, expected_output) -> None:
    """Tests whether problematic characters in body names are replaced as defined in `ENCODING_MAPPER`."""
    actual_output = custom_name_encode(body_name)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "input_arg, ndigits, expected_output",
    [
        (0.25, 1, 0.2),
        (0.25, 2, 0.25),
        (0.125, 1, 0.1),
        (0.1, 1, 0.1),
    ],
)
def test_bankers_rounding(input_arg, ndigits, expected_output) -> None:
    """Tests whether banker's rounding works as expected."""
    actual_output = bankers_rounding(value=input_arg, ndigits=ndigits)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "input_arg, ndigits, expected_output",
    [
        (0.25, 1, 0.3),
        (0.25, 2, 0.25),
        (0.125, 1, 0.1),
        (0.1, 1, 0.1),
    ],
)
def test_round_half_up(input_arg, ndigits, expected_output) -> None:
    """Tests whether round half up works as expected."""
    actual_output = round_half_up(value=input_arg, ndigits=ndigits)
    assert actual_output == expected_output


@pytest.mark.parametrize("ndigits", [0, -1, -5])
def test_round_half_up_raises_value_error_for_non_positive_ndigits(ndigits) -> None:
    """Tests whether a `ValueError` is raised when `ndigits` is less than 1."""
    with pytest.raises(ValueError):
        round_half_up(value=1.2345, ndigits=ndigits)


@pytest.mark.parametrize(
    "counter, body_identifier, expected_body_name, expected_geom_name",
    [
        (0, "product_a", "0_product_a", "0_product_a.box"),
        ("prefix", "sku#1", "prefix_sku\\#1", "prefix_sku\\#1.box"),
        (5, "a&b", "5_aANDb", "5_aANDb.box"),
    ],
)
def test_get_body_and_geom_name(counter, body_identifier, expected_body_name, expected_geom_name) -> None:
    """Tests whether body and geom names are created and encoded correctly."""
    actual_body_name, actual_geom_name = get_body_and_geom_name(counter=counter, body_identifier=body_identifier)
    assert actual_body_name == expected_body_name
    assert actual_geom_name == expected_geom_name


@pytest.mark.parametrize(
    "flb, size, unit, ndigits, expected_output",
    [
        ((0.0, 0.0, 0.0), (100, 100, 100), "mm", 6, ((0.05, 0.05, 0.05), (0.05, 0.05, 0.05))),
        ((0.0, 0.0, 0.0), (10, 10, 10), "cm", 6, ((0.05, 0.05, 0.05), (0.05, 0.05, 0.05))),
        ((10, 10, 0.0), (10, 10, 10), "cm", 3, ((0.05, 0.05, 0.05), (0.15, 0.15, 0.05))),
        ((1.5, 1.5, 0.0), (2.5, 2, 1), "dm", 1, ((0.1, 0.1, 0.1), (0.3, 0.3, 0.1))),
        ((1.5, 1.5, 0.0), (2.5, 2, 1), "dm", 2, ((0.13, 0.1, 0.05), (0.28, 0.25, 0.05))),
    ],
)
def test_mjcf_utils_convert_to_mjcf_coordinates(flb, size, unit, ndigits, expected_output) -> None:
    """Tests whether the conversion from FLB coordinates and the actual size is correctly done for the MuJoCo models."""
    actual_output = MJCFUtils.convert_to_mjcf_coordinates(flb=flb, size=size, unit=unit, ndigits=ndigits)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "flb, unit, ndigits, expected_output",
    [
        ((0.0, 0.0, 0.0), "mm", 6, (0.0, 0.0, 0.0)),
        ((1000, 500, 250), "mm", 3, (1.0, 0.5, 0.25)),
        ((10, 10, 10), "cm", 6, (0.1, 0.1, 0.1)),
        ((1.5, 1.5, 0.0), "dm", 2, (0.15, 0.15, 0.0)),
    ],
)
def test_mjcf_utils_convert_to_mjcf_pos(flb, unit, ndigits, expected_output) -> None:
    """Tests whether FLB coordinates are correctly converted to MJCF position coordinates."""
    actual_output = MJCFUtils.convert_to_mjcf_pos(flb=flb, unit=unit, ndigits=ndigits)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "input_arg, expected_output",
    [
        (1000, 1.0),
        (0.0, DEFAULT_WEIGHT_G / 1000),
        (1e-9, DEFAULT_WEIGHT_G / 1000),
        (234, 0.234),
        (230, 0.23),
        (31415, 31.415),
    ],
)
def test_mjcf_utils_convert_gramms_to_kg(input_arg, expected_output) -> None:
    """Tests whether the conversion of the mass from gramms to kilogramms is correct."""
    actual_output = MJCFUtils.convert_gramms_to_kg(input_arg)
    assert actual_output == expected_output


def test_mjcf_utils_export_model_to_mjcf_file(tmp_path: Path, mj_model: mujoco.MjModel) -> None:
    """Tests whether a MuJoCo model is exported to an MJCF file at the given path."""
    file_path = tmp_path / "exported_model.xml"

    MJCFUtils.export_model_to_mjcf_file(file_path=file_path, model=mj_model)

    assert file_path.is_file()
    assert "mjcf_utils_test_model" in file_path.read_text()


@pytest.mark.parametrize(
    "input_arg, expected_output",
    [((1, 2, 3), "1 2 3"), (("a", "b", "c"), "a b c"), ((0.1, 0.2, 0.3, 1), "0.1 0.2 0.3 1")],
)
def test_mjcf_utils_tuple_to_mjcf_string(input_arg, expected_output) -> None:
    """Tests whether tuples are correctly converted to strings for the mujoco modelling file."""
    actual_output = MJCFUtils.tuple_to_mjcf_string(input_arg)
    assert actual_output == expected_output
