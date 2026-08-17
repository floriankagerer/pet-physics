"""Tests for `EvaluationConfig`."""

from pet_physics.data_model.evaluation.pose.threshold_pose_delta import ThresholdPoseDelta
from pet_physics.data_model.evaluation.stability_check import StabilityCheck
from pet_physics.data_model.simulation.evaluation_config import EvaluationConfig


def _make_evaluation_config() -> EvaluationConfig:
    """Builds a representative `EvaluationConfig` instance used across the tests."""
    return EvaluationConfig(
        simulation_procedure="rigid",
        packforce_stability_threshold=ThresholdPoseDelta(max_x_delta_m=0.05),
        stability_check=StabilityCheck(check_type="wiggle"),
    )


def test_evaluation_config_stores_all_fields() -> None:
    """Constructing an `EvaluationConfig` should store all provided fields unchanged."""
    config = _make_evaluation_config()

    assert config.simulation_procedure == "rigid"
    assert config.packforce_stability_threshold.max_x_delta_m == 0.05
    assert config.stability_check.check_type == "wiggle"


def test_evaluation_config_survives_a_json_roundtrip() -> None:
    """Serializing to JSON and back should reproduce an equivalent `EvaluationConfig`."""
    config = _make_evaluation_config()

    restored_config = EvaluationConfig.from_json(config.to_json())

    assert restored_config == config
