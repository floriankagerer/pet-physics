"""Tests for the stability check configuration class."""

from pet_physics.data_model.evaluation.stability_check_configuration import StabilityCheckConfiguration


def test_initialization_of_stability_check_configuration() -> None:
    """Tests whether the initialization of a stability check configuration object works."""
    no_params = {}
    check_config = StabilityCheckConfiguration(parameters=no_params)

    # no settings
    assert check_config.parameters == {}

    # add a not recognized key to config
    check_config.add_parameter("foo", "bar")
    assert check_config.parameters == {}

    # now add some parameters in constructor
    new_params = {"answer": 42, "total_simulation_time_seconds": 3.14159265}
    check_config_2 = StabilityCheckConfiguration(parameters=new_params)

    assert check_config_2.parameters == {"total_simulation_time_seconds": 3.14159265}
    check_config_2.add_parameter("box_size_reduction_absolute_mm", 42)
    assert check_config_2.parameters == {
        "total_simulation_time_seconds": 3.14159265,
        "box_size_reduction_absolute_mm": 42,
    }
