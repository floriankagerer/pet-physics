"""A simple demo script."""

if __name__ == "__main__":
    from pathlib import Path

    from pet_physics.data_model.evaluation.stability_check import StabilityCheck
    from pet_physics.data_model.evaluation.stability_check_configuration import StabilityCheckConfiguration
    from pet_physics.data_model.teleport import Teleport
    from pet_physics.simulation import load_mujoco_model
    from pet_physics.simulation.callbacks.viewer_callback import ViewerCallback
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore

    model_path = Path(__file__).parents[1] / "src" / "pet_physics" / "mjcf_template" / "demo_world.xml"

    mj_model = load_mujoco_model(model_path)

    stability_check = StabilityCheck(
        check_type="one_by_one",
        check_configuration=StabilityCheckConfiguration(
            parameters={
                "total_simulation_time_seconds": 120,
                "box_size_reduction_absolute_mm": 0.1,
            },
        ),
    )

    teleport = Teleport(name="box", target_position=(0.6, 0.4, 0.5), initial_position=(2.0, 2.0, -0.094))

    pet_physics_core = PETPhysicsCore(
        model=mj_model,
        stability_check=stability_check,
        body_teleports=[teleport],
        total_simulation_time=120,
        teleport_interval=3,
        callbacks=[ViewerCallback()],
    )
    pet_physics_core.init_for_run(1 / 30)
    pet_physics_core.run()
