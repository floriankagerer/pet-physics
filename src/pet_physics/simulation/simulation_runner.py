"""This module is responsible for running a simulation."""

from __future__ import annotations

import multiprocessing
from collections.abc import Callable

import structlog

from pet_physics.constants import THRESHOLD_NORM_ANGULAR_ACCELERATION, THRESHOLD_NORM_LINEAR_ACCELERATION
from pet_physics.data_model.evaluation.pose.threshold_pose_delta import ThresholdPoseDelta
from pet_physics.data_model.model_configuration import ModelConfiguration
from pet_physics.data_model.modeling.collection_model_configuration import CollectionModelConfiguration
from pet_physics.data_model.modeling.mjcf.mujoco_model import MuJoCoModel
from pet_physics.data_model.serialization import to_dict
from pet_physics.data_model.simulation.evaluation_config import EvaluationConfig
from pet_physics.data_model.simulation.force_application_profile import ForceApplicationProfile
from pet_physics.data_model.teleport import Teleport
from pet_physics.evaluation.acceleration.evaluator_max_acceleration import EvaluatorMaxAcceleration
from pet_physics.evaluation.base_evaluator import BaseEvaluator
from pet_physics.evaluation.pose.evaluator_box_drop import EvaluatorBoxDrop
from pet_physics.evaluation.pose.evaluator_pose_delta import EvaluatorPoseDelta
from pet_physics.evaluation.simulation_run_evaluator import SimulationRunEvaluator
from pet_physics.modeling.model_generation.model_generator import ModelGenerator
from pet_physics.modeling.model_generation.model_generator_configuration import ModelGeneratorConfiguration
from pet_physics.simulation import load_mujoco_model_from_string
from pet_physics.simulation.callbacks.base_callback import BaseCallback
from pet_physics.simulation.callbacks.callback_utils import (
    get_collection_body_quantities_from_callbacks,
    is_callback_instance_in_list,
)
from pet_physics.simulation.callbacks.early_termination_callback import EarlyTerminationIfAnyBoxTouchesFloorCallback
from pet_physics.simulation.callbacks.force_applicator_callback import ForceApplicatorCallback
from pet_physics.simulation.callbacks.recorder_callback import RecorderCallback
from pet_physics.simulation.pet_physics_core import PETPhysicsCore
from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities
from pet_physics.simulation.physical_quantities.recorders.acceleration_recorder import AccelerationRecorder
from pet_physics.simulation.physical_quantities.recorders.base_recorder import BaseRecorder
from pet_physics.simulation.physical_quantities.recorders.pose_recorder import PoseRecorder
from pet_physics.simulation.procedure.simulation_procedure import SimulationProcedure

SimulationModel = MuJoCoModel
"""Type alias for the simulation models."""

logger = structlog.get_logger(__name__)


class SimulationRunner:
    """A `SimulationRunner` instance combines the generation of MuJoCo models for given configurations and starting
    a simulation run."""

    def __init__(
        self,
        procedure: SimulationProcedure,
        evaluation_config: EvaluationConfig,
        attempt_count: int = 2,
        force_application_profile_retrieve_function: Callable[[ModelConfiguration], ForceApplicationProfile]
        | None = None,
        activate_validation_of_simulation_run: bool = True,
    ) -> None:
        """Initializes the instance.

        Args:
            procedure: Defines the procedure of the simulaton, i.e., which configuration each run uses.
            evaluation_config: The configuration of the evaluation, which influences the simulation run.
            attempt_count: The number of attempts for a single model before the model is changed.
            force_application_profile_retrieve_function: A function that retrieves a force application profile for
                a given model configuration. If `None`, no force is applied during the simulation and consequently,
                no force application callback is injected.
            activate_validation_of_simulation_run: Whether to activate the validation of the simulation run.
        """
        self._procedure = procedure
        """Defines the procedure of the simulaton, i.e., which configuration each run uses."""
        logger.info(f"configure simulation runner with procedure '{self._procedure.name}'")

        self._evaluation_config = evaluation_config
        """The configuration of the evaluation, which influences the simulation run."""

        self._attempt_count = attempt_count
        """The number of attempts for a single model before the model is changed."""

        self._model_generator = ModelGenerator()
        """Object to generate the MuJoCo model, based on a given configuration."""

        self._force_application_profile_retrieve_function = force_application_profile_retrieve_function
        """A function that retrieves a force application profile for a given model configuration. If `None`, no force
        is applied during the simulation and consequently, no force application callback is injected."""

        self._activate_validation_of_simulation_run = activate_validation_of_simulation_run
        """Indicates whether the caller wants to activate the validation of the simulation run."""

        self._is_simulation_run_validation_activated = self._deduce_whether_simulation_run_validation_is_activated(
            activate_validation_of_simulation_run=self._activate_validation_of_simulation_run,
            force_application_profile_retrieve_function=self._force_application_profile_retrieve_function,
        )
        """Whether to activate the validation of the simulation run."""

    def _deduce_whether_simulation_run_validation_is_activated(
        self,
        activate_validation_of_simulation_run: bool,
        force_application_profile_retrieve_function: Callable[[ModelConfiguration], ForceApplicationProfile] | None,
        core_callbacks: list[BaseCallback] | None = None,
    ) -> bool:
        """Deduces whether the validation of a simulation run is activated. This is the case if in the constructor the
        activation flag is set to `True` and no force application will take place.

        Args:
            activate_validation_of_simulation_run: Whether to activate the validation of the simulation run.
            force_application_profile_retrieve_function: A function that retrieves a force application profile for
                a given model configuration. If `None`, no force is applied during the simulation and consequently,
                no force application callback is injected.
            core_callbacks: The core callbacks for this simulation run.

        Returns:
            Indicates whether the validation of a simulation run is activated.
        """
        is_force_application_profile_retrieve_function_given = force_application_profile_retrieve_function is not None
        is_force_applicator_callback_given = is_callback_instance_in_list(core_callbacks, ForceApplicatorCallback)

        if activate_validation_of_simulation_run and (
            is_force_application_profile_retrieve_function_given or is_force_applicator_callback_given
        ):
            msg = "simulation run validation is deactivated since a force application will take place"
            logger.warning(msg)

            return False

        return activate_validation_of_simulation_run

    @property
    def threshold_pose_delta(self) -> ThresholdPoseDelta:
        """The used threshold that defines whether a packing plan is stable."""
        return self._evaluation_config.packforce_stability_threshold

    def start(
        self,
        model_configurations: CollectionModelConfiguration,
        # collection_body_quantities: CollectionBodyQuantities, <-- explicitly add this!
        core_callbacks: tuple[RecorderCallback | BaseCallback, ...],
        evaluator_registrations: tuple[BaseEvaluator, ...],
    ) -> list[dict]:
        """Starts the simulation run for the given configurations.

        Args:
            model_configurations: All configurations that are used to create models in this simulation run.
            core_callbacks: Callbacks that are executed after every step of the `MuJoCo` core.
            evaluator_registrations: The evaluation callbacks for this simulation run.

        Returns:
            Contains the evaluation results for every bin in the bin packing response.
        """
        logger.info(f"model configurations result in '{len(model_configurations.configurations)}' simulation runs")
        response_evaluation_results = []

        self._is_simulation_run_validation_activated = self._deduce_whether_simulation_run_validation_is_activated(
            activate_validation_of_simulation_run=self._activate_validation_of_simulation_run,
            force_application_profile_retrieve_function=self._force_application_profile_retrieve_function,
            core_callbacks=core_callbacks,
        )

        model_generator_configs = self._procedure.model_generator_configurations
        for bin_name, bin_model_config in model_configurations.items():
            logger.info(f"start run for '{bin_name}'")
            bin_sim_result = self._start_single(
                model_generator_configs, bin_model_config, core_callbacks, evaluator_registrations
            )
            bin_sim_result.update({"bin_name": bin_name})
            response_evaluation_results.append(bin_sim_result)

        return response_evaluation_results

    def _mp_check_whether_stop_event_is_set(
        self, stop_event: multiprocessing.synchronize.Event, process_name: str
    ) -> None:
        """Blocks until the stop event is set, logging progress every 30 seconds.

        Args:
            stop_event: Indicates whether the process should terminate.
            process_name: The name of a process.
        """
        counter = 0
        while not stop_event.wait(1):
            counter += 1
            if counter % 30 == 0:
                logger.info(f"process '{process_name}' is still running")
                counter = 0
        logger.info("stop event received")

    def _inject_box_names_to_sizes_mapping_to_evaluator_box_drop(
        self, evaluator_registrations: list[BaseEvaluator], model_configuration: ModelConfiguration
    ) -> None:
        """Injects the mapping of box names to their sizes to the ``EvaluatorBoxDrop`` instance in the given list of evaluation callbacks.

        Since we get the mapping from the model configuration, we need to inject this mapping before the simulation
        run, and not when defining the simulation runner instance.

        Args:
            evaluator_registrations: The evaluation callbacks for this simulation run.
            model_configuration: The model configuration for a single bin.
        """
        for evaluator_instance in evaluator_registrations:
            if isinstance(evaluator_instance, EvaluatorBoxDrop):
                evaluator_instance.body_name_to_size_mapping = model_configuration.get_box_names_to_sizes_mapping()
                logger.info(f"injected body name to size mapping to '{evaluator_instance.__class__.__name__}'")

    def _inject_box_names_to_sizes_mapping_to_early_termination_callback(
        self, core_callbacks: list[RecorderCallback | BaseCallback], model_configuration: ModelConfiguration
    ) -> None:
        """Injects the mapping of box names to their sizes to the ``EarlyTerminationIfAnyBoxTouchesFloorCallback`` instance.

        Since we get the mapping from the model configuration, we need to inject this mapping before the simulation
        run, and not when defining the simulation runner instance.

        Args:
            core_callbacks: The core callbacks for this simulation run.
            model_configuration: The model configuration for a single bin.
        """
        for callback_instance in core_callbacks:
            if isinstance(callback_instance, EarlyTerminationIfAnyBoxTouchesFloorCallback):
                callback_instance.body_name_to_size_mapping = model_configuration.get_box_names_to_sizes_mapping()
                logger.info(f"injected body name to size mapping to '{callback_instance.__class__.__name__}' callback")

    def _inject_force_applicator_callback_based_on_force_application_profile(
        self, core_callbacks: list[RecorderCallback | BaseCallback], model_configuration: ModelConfiguration
    ) -> None:
        """Injects the force application profile to the ``ForceApplicatorCallback`` instance in the given list of core callbacks.

        Since we use the model configuration to retrieve the correct force application profile, we need to define the
        force applicator callback here.

        Args:
            core_callbacks: The core callbacks for this simulation run.
            model_configuration: The model configuration for a single bin.
        """
        if self._force_application_profile_retrieve_function is None:
            return None

        force_application_profile = self._force_application_profile_retrieve_function(model_configuration)
        force_applicator_callback = ForceApplicatorCallback(force_application_profile)

        core_callbacks.append(force_applicator_callback)
        logger.info("injected force applicator callback to core callbacks")

    def _start_single(
        self,
        generator_configurations: list[ModelGeneratorConfiguration],
        model_configuration: ModelConfiguration,
        core_callbacks: tuple[RecorderCallback | BaseCallback, ...],
        evaluator_registrations: tuple[BaseEvaluator, ...],
    ) -> dict:
        """This method takes care to run the simulation for a single model configuration. This contains the generation
        of a model, an actual run of the simulation, calling the evaluation callbacks and taking care of the results.

        It also takes into consideration to perform the required taks that are related to the simulation mode.

        Args:
            generator_configurations: A list of model configurations that configure the model generator.
            model_configuration: The model configuration for a single bin.
            core_callbacks: Callbacks that are executed after every step of the `MuJoCo` core.
            evaluator_registrations: The evaluation callbacks for this simulation run.

        Returns:
            The evaluation result of this single simulation run.
        """
        simulation_successful = False
        TIMEOUT_AFTER_STOP_EVENT_SECONDS = 5

        for active_generator_config in generator_configurations:
            core_callbacks_this_run = list(core_callbacks)
            evaluator_registrations = list(evaluator_registrations)
            simulation_model = self._model_generator.generate(active_generator_config, model_configuration)
            teleports = model_configuration.teleports
            teleport_interval = 0.7
            total_simulation_time = (len(model_configuration.boxes) + 1) * teleport_interval
            self._inject_box_names_to_sizes_mapping_to_early_termination_callback(
                core_callbacks_this_run, model_configuration
            )
            self._inject_force_applicator_callback_based_on_force_application_profile(
                core_callbacks_this_run, model_configuration
            )
            self._inject_box_names_to_sizes_mapping_to_evaluator_box_drop(evaluator_registrations, model_configuration)
            stop_event = multiprocessing.Event()

            queue = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=self._mp_run_single_simulation,
                args=(
                    stop_event,
                    queue,
                    simulation_model,
                    teleports,
                    total_simulation_time,
                    teleport_interval,
                    core_callbacks_this_run,
                    evaluator_registrations,
                ),
                name=f"process-physics_{model_configuration.model_name}",
            )

            process.start()

            self._mp_check_whether_stop_event_is_set(stop_event, process.name)

            process.join(timeout=TIMEOUT_AFTER_STOP_EVENT_SECONDS)

            simulation_successful, result_evaluation = queue.get(block=True)

            # extend result of evaluation
            result_evaluation.update(
                {
                    "generator_configuration": active_generator_config.configuration_name,
                    "run_is_valid": simulation_successful,
                }
            )
            logger.info(result_evaluation)

            process.kill()

            # finish for loop if run is valid
            if simulation_successful:
                break

        if not simulation_successful:
            logger.warning("unable to produce a valid simulation run with this procedure")

        return result_evaluation

    def _mp_run_single_simulation(
        self,
        stop_event: multiprocessing.synchronize.Event,
        queue: multiprocessing.Queue,
        simulation_model: SimulationModel,
        teleports: list[Teleport],
        total_simulation_time: float,
        teleport_interval: float,
        core_callbacks: list[RecorderCallback | BaseCallback],
        evaluator_registrations: list[BaseEvaluator],
    ) -> None:
        """This method should be called if you want to call `_run_single_simulation` in a `multiprocessing.Process`
        instance. This method works as wrapper around `_run_single_simulation`.

        **Instead of returning a result, the result is put to the given `queue`.**

        Args:
            stop_event: Indicates whether the process should terminate.
            queue: The queue to that the simulation result is put.
            simulation_model: The simulation model for this run.
            teleports: A list of body teleports that are applied during the simulation.
            total_simulation_time: The total simulation time in seconds.
            teleport_interval: The time that elapses between two teleports in seconds.
            core_callbacks: Callbacks that are executed after every step of the `MuJoCo` core.
            evaluator_registrations: The evaluation callbacks for this simulation run.
        """
        run_is_valid, result_evaluation = self._run_single_simulation(
            simulation_model,
            teleports,
            total_simulation_time,
            teleport_interval,
            core_callbacks,
            evaluator_registrations,
        )

        queue.put((run_is_valid, result_evaluation))
        queue.close()
        stop_event.set()

    def _extend_callbacks_with_run_validation_callbacks(
        self,
        callbacks: list[RecorderCallback | BaseCallback],
        run_validation_recorders: list[BaseRecorder],
    ) -> tuple[list[RecorderCallback | BaseCallback], CollectionBodyQuantities]:
        """Extends the given callbacks with callbacks that are required to decide whether a simulation run is valid.

        This is done by adding ``RecorderCallback`` instances for the given recorders.

        Args:
            callbacks: The list of callbacks that should be extended.
            run_validation_recorders: The recorders that are required to decide whether a simulation run is valid.
            For each of these recorders, a `RecorderCallback` instance is created and added to the callbacks.

        Returns:
            The extended list of callbacks and the collection of body quantities used by the recorder based callbacks
                in the simulation.
        """
        extended_callbacks = []
        extended_callbacks.extend(callbacks)

        collection_body_quantities = get_collection_body_quantities_from_callbacks(callbacks)
        if collection_body_quantities is None:
            # no recorder based callback is present
            collection_body_quantities = CollectionBodyQuantities()

        for recorder in run_validation_recorders:
            try:
                # create a recorder based callback
                # if this recorder based callback is registered in the collection body quantities, we do nothing
                recorder_callback = RecorderCallback(recorder, collection_body_quantities)
                extended_callbacks.append(recorder_callback)

            except ValueError:
                # this recorder based callback is already registered
                pass

        return extended_callbacks, collection_body_quantities

    def _run_single_simulation(
        self,
        simulation_model: SimulationModel,
        teleports: list[Teleport],
        total_simulation_time: float,
        teleport_interval: float,
        core_callbacks: list[RecorderCallback | BaseCallback],
        evaluator_registrations: list[BaseEvaluator],
    ) -> tuple[bool, dict]:
        """Runs a simulation with the specified model, teleports, total simulation time and interval between
        two teleports.

        Note that it is tried to get a valid run as often as you specified in ``self._attempt_count``.

        Args:
            simulation_model: The simulation model for this run.
            teleports: A list of body teleports that are applied during the simulation.
            total_simulation_time: The total simulation time in seconds.
            teleport_interval: The time that elapses between two teleports in seconds.
            core_callbacks: Callbacks that are executed after every step of the ``MuJoCo`` core.
            evaluator_registrations: The evaluation callbacks for this simulation run.

        Returns:
            A tuple of (run_is_valid, result_evaluation) where run_is_valid indicates whether the
                simulation run was successful and result_evaluation contains the evaluation result.
        """
        # add callbacks to detect whether a simulation run is valid
        extended_core_callbacks, collection_body_quantities = self._extend_callbacks_with_run_validation_callbacks(
            core_callbacks, [AccelerationRecorder, PoseRecorder]
        )

        # initialize the simulation run evaluator
        result_evaluation = {}
        sim_run_evaluator = SimulationRunEvaluator()
        evaluation_names = []
        for evaluator_instance in evaluator_registrations:
            evaluation_names.append(evaluator_instance.cl_name)
            sim_run_evaluator.register_evaluator(evaluator_instance)

        # initialize the simulation core
        stability_check = self._evaluation_config.stability_check
        model = load_mujoco_model_from_string(simulation_model.to_xml_string())
        core = PETPhysicsCore(
            model, stability_check, teleports, total_simulation_time, teleport_interval, extended_core_callbacks
        )

        remaining_attempts = self._attempt_count
        run_is_valid = False
        while (not run_is_valid) and (remaining_attempts > 0):
            remaining_attempts -= 1

            logger.debug(f"start simulation run for model - total sim time={total_simulation_time} seconds")
            core.init_for_run(1 / 5)
            core.run()

            if self._is_run_validation_deactivated or self._is_run_valid(collection_body_quantities):
                run_is_valid = True
                result_stability, stability_additional_information = self._evaluate_stability_of_packing_plan(
                    collection_body_quantities, teleports
                )
                result_evaluation = self._evaluate_run(collection_body_quantities, sim_run_evaluator, evaluation_names)

                result_evaluation.update(result_stability)
                result_evaluation["additional_information"] = {
                    "stability_threshold": to_dict(self.threshold_pose_delta)
                }
                if not result_stability.get("is_stable"):
                    result_evaluation["additional_information"].update(stability_additional_information)

            else:
                logger.warning("run is not valid - reset core and run simulation again")

        return run_is_valid, result_evaluation

    @property
    def _is_run_validation_deactivated(self) -> bool:
        """Whether the validation of a simulation run is deactivated."""
        return not self._is_simulation_run_validation_activated

    def _is_run_valid(self, collection_body_quantities: CollectionBodyQuantities) -> bool:
        """
        Evaluates and decides whether a simulation run is valid.

        Args:
            collection_body_quantities: The collection of body quantities that are recorded during the simulation run.

        Returns:
            Indicates whether a simulation run is valid.
        """
        run_is_valid = True
        evaluator_max_acc = EvaluatorMaxAcceleration()

        max_acceleration_result = evaluator_max_acc.evaluate(collection_body_quantities=collection_body_quantities)
        logger.info(f"run validation result: {to_dict(max_acceleration_result)}")

        if max_acceleration_result.maximal_value_linear_acceleration > THRESHOLD_NORM_LINEAR_ACCELERATION:
            logger.warning("max value of linear acceleration is greater than threshold")
            run_is_valid = False
        if max_acceleration_result.maximal_value_angular_acceleration > THRESHOLD_NORM_ANGULAR_ACCELERATION:
            logger.warning("max value of angular acceleration is greater than threshold")
            run_is_valid = False

        return run_is_valid

    def _evaluate_stability_of_packing_plan(
        self, collection_body_quantities: CollectionBodyQuantities, teleports: list[Teleport]
    ) -> tuple[dict[str, bool | dict], dict[str, str]]:
        """
        Evaluates and decides whether a packing plan is stable.

        Args:
            collection_body_quantities: The collection of body quantities that are recorded during the simulation run.
            teleports: The teleports that are applied during the simulation.

        Returns:
            A tuple containing a dictionary indicating stability and a dictionary with additional stability information.
        """
        evaluator_pose_delta = EvaluatorPoseDelta(teleports)

        pose_delta_result = evaluator_pose_delta.evaluate(collection_body_quantities=collection_body_quantities)
        is_stable, stability_additional_information = pose_delta_result.are_records_within_threshold(
            self.threshold_pose_delta
        )

        return {"is_stable": is_stable, EvaluatorPoseDelta.cl_name: to_dict(pose_delta_result)}, {
            "stability_additional_information": stability_additional_information
        }

    def _evaluate_run(
        self,
        collection_body_quantities: CollectionBodyQuantities,
        evaluator: SimulationRunEvaluator,
        evaluation_names: list[str],
    ) -> dict:
        """
        Evaluates the simulation run by using the defined core callbacks and evaluations.

        Args:
            collection_body_quantities: The collection of body quantities that are recorded during the simulation run.
            evaluator: The evaluator of this simulation run.
            evaluation_names: The name with that the evaluators have been registered.

        Returns:
            The evaluation result of this simulation run.
        """
        results_run_evaluation = {}

        for eval_name in evaluation_names:
            result = evaluator.eval(eval_name, collection_body_quantities=collection_body_quantities)
            results_run_evaluation[eval_name] = to_dict(result)

        logger.info(f"results of this run: {results_run_evaluation}")

        return results_run_evaluation
