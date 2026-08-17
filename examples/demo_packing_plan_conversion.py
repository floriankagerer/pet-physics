"""This script demonstrates how to convert a packing plan into a collection of model configurations."""

from pathlib import Path

import structlog

from pet_physics.conversion.bed_bpp.configuration_factory_from_bed_bpp import (
    create_collection_model_configurations_from_packing_plans,
)
from pet_physics.data_model.evaluation.stability_check import StabilityCheck
from pet_physics.data_model.evaluation.stability_check_configuration import StabilityCheckConfiguration
from pet_physics.data_model.model_configuration import ModelConfiguration
from pet_physics.data_model.packing.collection_packing_plan import CollectionPackingPlan
from pet_physics.modeling.model_generation.model_generator import ModelGenerator
from pet_physics.modeling.model_generation.model_generator_configuration import RigidNewton
from pet_physics.utils.io_helpers import get_output_dir_for_model_configuration
from pet_physics.utils.logging_setup import setup_logging

logger = structlog.get_logger(__name__)
setup_logging("info")

_STABILITY_CHECK = StabilityCheck(
    check_type="one_by_one",
    check_configuration=StabilityCheckConfiguration(
        parameters={
            "total_simulation_time_seconds": 10,
            "box_size_reduction_absolute_mm": 0.1,
        },
    ),
)


def get_model_configuration_and_mujoco_model_str(
    packing_plan_path: Path, packing_plan_index: int
) -> tuple[ModelConfiguration, str]:
    """Return the `ModelConfiguration` and MuJoCo XML string for a packing plan index.

    Loads a `CollectionPackingPlan` from `packing_plan_path`, converts all packing plans to model configurations
    (writing model XML files to the output directory if missing), and returns the `ModelConfiguration` together with
    the MuJoCo model XML string for the packing plan at `packing_plan_index`.

    Args:
        packing_plan_path: Path to the bed-bpp packing plan JSON file.
        packing_plan_index: Index of the packing plan whose model should be returned.

    Returns:
        A tuple `(ModelConfiguration, str)` with the selected model configuration and the MuJoCo model XML string.

    Raises:
        ValueError: If `packing_plan_index` is greater than or equal to the number of packing plans in the collection.
            Negative indices are considered invalid
    """
    collection_packing_plan = CollectionPackingPlan.from_file(packing_plan_path)

    if packing_plan_index < 0:
        logger.error("Packing plan index must not be smaller than zero.")
    elif packing_plan_index >= len(collection_packing_plan.packing_plans):
        msg = (
            f"Packing plan index is too big. Index must be within [0, {len(collection_packing_plan.packing_plans) - 1}]"
        )
        logger.warning(msg)
        raise ValueError(msg)

    model_dir_for_packing_plan = get_output_dir_for_model_configuration(
        packing_plan_path=packing_plan_path, write_into_home_subdir=True
    )
    collection_model_configuration = create_collection_model_configurations_from_packing_plans(
        packing_plans=collection_packing_plan.packing_plans,
        stability_check=_STABILITY_CHECK,
        body_special_coloring=None,
        model_bin_as_freejoint_body=False,
    )

    # save all models
    for model_configuration_index, model_configuration in enumerate(collection_model_configuration.configurations):
        model_path = model_dir_for_packing_plan / f"{packing_plan_path.stem}-{model_configuration.model_name}.xml"

        if not model_path.exists():
            model_dir_for_packing_plan.mkdir(parents=True, exist_ok=True)
            model_generator = ModelGenerator()
            model = model_generator.generate(RigidNewton(), model_configuration)
            model_path.write_text(model.to_xml_string())
            logger.info(f"Stored model in '{model_path}'.")

        if model_configuration_index == packing_plan_index:
            restore_model_from_path = model_path

    # select specific model configuration
    model_configuration = collection_model_configuration.configurations[packing_plan_index]
    model_str = restore_model_from_path.read_text()

    return model_configuration, model_str


if __name__ == "__main__":
    from pet_physics.simulation import load_mujoco_model_from_string
    from pet_physics.simulation.callbacks.viewer_callback import ViewerCallback
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore

    packing_plan_path = Path(__file__).parents[1] / "examples" / "packing_plan_5-bed-bpp.json"

    model_configuration, mj_model_str = get_model_configuration_and_mujoco_model_str(
        packing_plan_path=packing_plan_path,
        packing_plan_index=0,
    )

    body_teleports = model_configuration.teleports
    teleport_every = 3
    total_simulation_time = (1 + len(model_configuration.boxes)) * teleport_every + 50

    # visualize model
    mj_model = load_mujoco_model_from_string(mj_model_str)
    teleport_every = 3
    total_simulation_time = (1 + len(model_configuration.boxes)) * teleport_every + 20

    callbacks = [ViewerCallback()]

    pet_physics_core = PETPhysicsCore(
        model=mj_model,
        stability_check=_STABILITY_CHECK,
        body_teleports=model_configuration.teleports,
        total_simulation_time=total_simulation_time,
        teleport_interval=teleport_every,
        callbacks=callbacks,
    )
    pet_physics_core.init_for_run(1 / 20)
    pet_physics_core.run()
