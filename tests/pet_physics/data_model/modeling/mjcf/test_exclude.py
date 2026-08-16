import pytest

from pet_physics.data_model.modeling.mjcf.exclude import Exclude


@pytest.mark.parametrize(
    "exclude, expected_xml_string",
    [
        (Exclude(body1="body1", body2="body2"), '<exclude body1="body1" body2="body2" />'),
        (Exclude(body1="body1", body2="body2", name="foobar"), '<exclude body1="body1" body2="body2" name="foobar" />'),
        (Exclude(body1="body1", body2="body2", name=None), '<exclude body1="body1" body2="body2" />'),
        (
            Exclude(name="test_name", body1="body1", body2="body2"),
            '<exclude body1="body1" body2="body2" name="test_name" />',
        ),
    ],
)
def test_exclude_to_xml_string(exclude: Exclude, expected_xml_string: str) -> None:
    assert exclude.to_xml_string() == expected_xml_string
