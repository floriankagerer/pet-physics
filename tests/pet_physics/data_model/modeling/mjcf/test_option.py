import pytest

from pet_physics.data_model.modeling.mjcf.option import Option


@pytest.mark.parametrize(
    "option, expected_xml_string",
    [
        (Option(), "<option />"),
        (Option(integrator="implicitfast", cone="elliptic"), '<option integrator="implicitfast" cone="elliptic" />'),
        (
            Option(integrator="implicitfast", cone="elliptic", solver="CG"),
            '<option integrator="implicitfast" cone="elliptic" solver="CG" />',
        ),
    ],
)
def test_option_to_xml_string(option: Option, expected_xml_string: str):
    assert option.to_xml_string() == expected_xml_string
