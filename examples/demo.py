"""A simple demo script."""

if __name__ == "__main__":
    from pathlib import Path

    from pet_physics.simulation import load_mujoco_model
    from pet_physics.simulation.callbacks.viewer_callback import ViewerCallback
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore

    model_path = Path(__file__).parents[1] / "src" / "pet_physics" / "mjcf_template" / "demo_world.xml"

    mj_model = load_mujoco_model(model_path)

    pet_physics_core = PETPhysicsCore(
        model=mj_model,
        stability_check=None,
        body_teleports=None,
        total_simulation_time=120,
        teleport_interval=None,
        callbacks=[ViewerCallback()],
    )
    pet_physics_core.init_for_run(1 / 30)
    pet_physics_core.run()
