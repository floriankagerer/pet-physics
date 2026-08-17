"""A script that demonstrates the force application."""

from pathlib import Path

import structlog

from pet_physics.constants import GRAVITY
from pet_physics.conversion.bed_bpp.configuration_factory_from_bed_bpp import (
    create_collection_model_configurations_from_packing_plans,
)
from pet_physics.data_model.evaluation.stability_check import StabilityCheck, StabilityCheckConfiguration
from pet_physics.data_model.model_configuration import ModelConfiguration
from pet_physics.data_model.packing.collection_packing_plan import CollectionPackingPlan
from pet_physics.data_model.simulation.force_application_profile import ForceApplicationProfile
from pet_physics.modeling.model_generation.model_generator import ModelGenerator
from pet_physics.modeling.model_generation.model_generator_configuration import RigidNewton
from pet_physics.simulation.callbacks.force_applicator_callback import ForceApplicatorCallback
from pet_physics.simulation.force_application.force_application_profile_provider import ForceApplicationProfileProvider
from pet_physics.utils.io_helpers import get_output_dir_for_model_configuration

logger = structlog.get_logger(__name__)

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
    # TODO(flo): Make two functions for this => parametrize whether to load an existing model or not; parametrize
    #   whether a specific model configuration is returned or the entire collection.
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
        model_bin_as_freejoint_body=True,
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


def get_force_application_profile(
    model_configuration: ModelConfiguration, initial_time_offset: float = 0.0
) -> ForceApplicationProfile:
    """
    Returns a force application profile that is suitable for the given model configuration. Suitable means in this case
    that it is validated with respect to the model configuration, i.e., the force targets exist in the model and these
    bodies are modelled as freejoint bodies.

    Args:
        model_configuration: The model configuration of the simulation.
        initial_time_offset: Some time offset that is added to all application time.

    Returns:
        The force application profile for the simulation.
    """
    if model_configuration.total_mass_of_carrier_and_boxes is None:
        raise ValueError("Check the mass of the carrier and boxes in the model configuration.")

    force_application_profile_provider = ForceApplicationProfileProvider()

    force_application_profile = ForceApplicationProfile()

    for application_time_offset, magnitude_factor in zip(
        [2.0, 4.0, 7.0, 9.5, 12.0, 14.5, 17.0],
        [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 2.0],
    ):
        # compute magnitude based on total mass
        magnitude = model_configuration.total_mass_of_carrier_and_boxes * GRAVITY * magnitude_factor

        # get radial profile
        radial_profile = force_application_profile_provider.get_radial_profile(
            magnitude=magnitude,
            application_time_offset=initial_time_offset + application_time_offset,
            target=model_configuration.carrier.name,
        )

        force_application_profile += radial_profile

    # set force targets
    sorted_target_names = [model_configuration.carrier.name] * force_application_profile.number_forces
    force_application_profile.set_force_targets(
        sorted_target_names=sorted_target_names, target_validation=model_configuration
    )

    return force_application_profile


if __name__ == "__main__":
    from pet_physics.simulation import load_mujoco_model_from_string
    from pet_physics.simulation.callbacks.viewer_callback import ViewerCallback
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore
    from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities
    from pet_physics.utils.logging_setup import setup_logging

    setup_logging("info")

    packing_plan_path = Path(__file__).parents[1] / "examples" / "packing_plan_a.json"

    model_configuration, mj_model_str = get_model_configuration_and_mujoco_model_str(
        packing_plan_path=packing_plan_path,
        packing_plan_index=0,
    )
    mj_model = load_mujoco_model_from_string(mj_model_str)

    teleport_every = 0.5
    time_until_all_boxes_are_placed = teleport_every * len(model_configuration.teleports)
    total_simulation_time = time_until_all_boxes_are_placed * 2.5

    # define force application profile
    force_application_profile = get_force_application_profile(
        model_configuration,
        initial_time_offset=time_until_all_boxes_are_placed + 2.0,
    )

    collection_body_quantities = CollectionBodyQuantities()
    callbacks = [
        ViewerCallback(),
        ForceApplicatorCallback(force_application_profile),
    ]

    pet_physics_core = PETPhysicsCore(
        model=mj_model,
        stability_check=_STABILITY_CHECK,
        body_teleports=model_configuration.teleports,
        total_simulation_time=total_simulation_time,
        teleport_interval=teleport_every,
        callbacks=callbacks,
    )
    pet_physics_core.init_for_run(1 / 30)
    pet_physics_core.run()
