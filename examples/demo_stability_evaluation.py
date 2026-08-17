"""A script that demonstrates the static stability assessment, evaluating multiple packing plans."""

import json
from pathlib import Path
from typing import Literal

import structlog

from pet_physics.conversion.bed_bpp.configuration_factory_from_bed_bpp import (
    create_collection_model_configurations_from_packing_plans,
)
from pet_physics.data_model.evaluation.pose.threshold_pose_delta import ThresholdPoseDelta
from pet_physics.data_model.evaluation.stability_check import StabilityCheck, StabilityCheckConfiguration
from pet_physics.data_model.modeling.collection_model_configuration import CollectionModelConfiguration
from pet_physics.data_model.packing.collection_packing_plan import CollectionPackingPlan
from pet_physics.data_model.simulation.evaluation_config import EvaluationConfig
from pet_physics.modeling.model_generation.model_generator import ModelGenerator
from pet_physics.modeling.model_generation.model_generator_configuration import RigidNewton
from pet_physics.simulation.procedure.simulation_procedure import SimulationProcedureNames
from pet_physics.utils.io_helpers import get_output_dir_for_model_configuration

logger = structlog.get_logger(__name__)


def _get_path_of_evaluation_results(packing_plan_path: Path) -> Path:
    """Returns the path to that the evaluation results are written.

    Args:
        packing_plan_path: The path to the packing plan file

    Returns:
        The path to that the evaluation results are written.
    """
    this_file_path = Path(__file__)
    output_dir_in_examples = this_file_path.parent / "output"
    return output_dir_in_examples / f"{this_file_path.stem}-{packing_plan_path.stem}.json"


def _write_result_of_simulation_runner(file_path: Path, results: dict) -> None:
    """Writes the results to the specified file path."""
    # create file if it does not exist
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

    with open(file_path, "w") as file:
        json.dump(results, file)


def get_example_evaluation_configuration(
    stability_check_check_type: Literal["static", "one_by_one"],
    total_simulation_time_seconds: float,
) -> EvaluationConfig:
    """
    Returns the evaluation configuration with the specified parameters. The evaluation configuration defines

    1. the used *simulation procedure*,
    2. the thresholds for the classification of *stability*, and
    3. the definition of the *stability check*.

    Args:
        stability_check_check_type (Literal["static", "one_by_one"]): The type of the stability check, either "static"
            or "one_by_one".
        total_simulation_time_seconds (float): The total simulation time in seconds for the stability check.

    Returns:
        EvaluationConfig: The evaluation configuration.
    """

    SIMULATION_PROCEDURE_NAME: SimulationProcedureNames = "rigid"

    THRESHOLD_STABILITY_POSE_DELTA = ThresholdPoseDelta(
        max_x_delta_m=0.02,
        max_y_delta_m=0.02,
        max_z_delta_m=0.02,
        max_tiltedness_degrees=20,
    )

    STABILITY_CHECK = StabilityCheck(
        check_type=stability_check_check_type,
        check_configuration=StabilityCheckConfiguration(
            parameters={
                "total_simulation_time_seconds": total_simulation_time_seconds,
                "box_size_reduction_absolute_mm": 0.1,
            }
        ),
    )
    # # # # # # # # # # # # # # # # # # # # # # # # #
    eval_config = EvaluationConfig(
        simulation_procedure=SIMULATION_PROCEDURE_NAME,
        packforce_stability_threshold=THRESHOLD_STABILITY_POSE_DELTA,
        stability_check=STABILITY_CHECK,
    )

    return eval_config


def get_collection_model_configuration(
    packing_plan_path: Path,
    stability_check: StabilityCheck,
    body_special_coloring: dict[str, str] | None = None,
) -> CollectionModelConfiguration:
    """TBD"""

    # TODO(flo): Make two functions for this => parametrize whether to load an existing model or not; parametrize
    #   whether a specific model configuration is returned or the entire collection.
    #   combine with `get_model_configuration_and_mujoco_model_str`
    collection_packing_plan = CollectionPackingPlan.from_file(packing_plan_path)

    model_dir_for_packing_plan = get_output_dir_for_model_configuration(
        packing_plan_path=packing_plan_path, write_into_home_subdir=True
    )
    collection_model_configuration = create_collection_model_configurations_from_packing_plans(
        packing_plans=collection_packing_plan.packing_plans,
        stability_check=stability_check,
        body_special_coloring=body_special_coloring,
        model_bin_as_freejoint_body=True,
    )

    # save all models
    for model_configuration in collection_model_configuration.configurations:
        model_path = model_dir_for_packing_plan / f"{packing_plan_path.stem}-{model_configuration.model_name}.xml"

        if not model_path.exists():
            model_dir_for_packing_plan.mkdir(parents=True, exist_ok=True)
            model_generator = ModelGenerator()
            model = model_generator.generate(RigidNewton(), model_configuration)
            model_path.write_text(model.to_xml_string())
            logger.info(f"Stored model in '{model_path}'.")

    return collection_model_configuration


if __name__ == "__main__":
    from pet_physics.simulation.callbacks.recorder_callback import RecorderCallback
    from pet_physics.simulation.callbacks.viewer_callback import ViewerCallback
    from pet_physics.simulation.physical_quantities.collection_body_quantities import (
        CollectionBodyQuantities,
    )
    from pet_physics.simulation.physical_quantities.recorders.force_penetration_recorder import (
        ForcePenetrationRecorder,
    )
    from pet_physics.simulation.procedure import get_simulation_procedure
    from pet_physics.simulation.simulation_runner import SimulationRunner
    from pet_physics.utils.logging_setup import setup_logging

    setup_logging("info")

    packing_plan_path = Path(__file__).parents[1] / "examples" / "packing_plan_5-bed-bpp.json"
    # packing_plan_path = Path(__file__).parents[1] / "examples" / "packing_plan_a.json"
    example_evaluation_result_path = _get_path_of_evaluation_results(packing_plan_path)

    evaluation_config = get_example_evaluation_configuration(
        stability_check_check_type="one_by_one", total_simulation_time_seconds=45.0
    )
    simulation_procedure_name = evaluation_config.simulation_procedure
    threshold_stability = evaluation_config.packforce_stability_threshold
    stability_check = evaluation_config.stability_check

    model_configurations = get_collection_model_configuration(
        packing_plan_path=packing_plan_path,
        stability_check=evaluation_config.stability_check,
    )
    logger.info(f"bin packing response results in '{len(model_configurations.configurations)}' bins")

    simulation_procedure = get_simulation_procedure(simulation_procedure_name)

    collection_body_quantities = CollectionBodyQuantities()
    core_callbacks = (
        ViewerCallback(),
        RecorderCallback(ForcePenetrationRecorder, collection_body_quantities),
    )
    evaluator_registrations = ()
    simulation_runner = SimulationRunner(simulation_procedure, evaluation_config)
    results = simulation_runner.start(model_configurations, core_callbacks, evaluator_registrations)

    _write_result_of_simulation_runner(example_evaluation_result_path, results)
