"""Tests for the stability check class."""

from pet_physics.data_model.evaluation.stability_check import StabilityCheck
from pet_physics.data_model.evaluation.stability_check_configuration import StabilityCheckConfiguration


def test_initialization_of_stability_check() -> None:
    """Tests whether the initialization of a stability check object works."""
    no_params = {}
    empty_config = StabilityCheckConfiguration(parameters=no_params)
    stability_check = StabilityCheck(check_type="static", check_configuration=empty_config)

    assert stability_check.is_type_static
    assert not stability_check.is_type_one_by_one
    assert not stability_check.is_type_wiggle
    assert stability_check.check_configuration.parameters == {}

    stability_check.check_configuration.add_parameter("total_simulation_time_seconds", 42)

    assert stability_check.check_configuration.parameters == {"total_simulation_time_seconds": 42}
