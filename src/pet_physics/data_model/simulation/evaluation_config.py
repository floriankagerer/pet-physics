"""Data class for the configuration of a simulation evaluation."""

from dataclasses import dataclass

from dataclasses_json import dataclass_json

from pet_physics.data_model.evaluation.pose.threshold_pose_delta import ThresholdPoseDelta
from pet_physics.data_model.evaluation.stability_check import StabilityCheck
from pet_physics.simulation.procedure.simulation_procedure import SimulationProcedureNames


@dataclass_json
@dataclass
class EvaluationConfig:
    """Configuration for a PETPhysics evaluation.

    Holds the simulation procedure, the stability thresholds, and the stability check used to classify a packing plan
    as stable or unstable.

    Attributes:
        simulation_procedure: The simulation procedure used to evaluate the bin packing response.
        packforce_stability_threshold: Threshold that defines whether a packing plan is classified as stable.
        stability_check: The stability check used to evaluate the bin packing response.
    """

    simulation_procedure: SimulationProcedureNames
    packforce_stability_threshold: ThresholdPoseDelta
    stability_check: StabilityCheck
