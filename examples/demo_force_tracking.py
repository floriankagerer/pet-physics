"""A script that demonstrates the force tracking."""

from pet_physics.data_model.teleport import Teleport

MJ_MODEL = """
<mujoco>
    <asset>
        <texture name="sky" type="skybox" builtin="flat" width="300" height="300" rgb1="0.9 0.9 0.9" />
        <material name="grid" texture="grid" texrepeat="2 2" texuniform="true" reflectance="0.0" />
        <texture name="grid" type="2d" builtin="checker" width="300" height="300" rgb1="0.1 0.2 0.3"
            rgb2="0.2 0.3 0.4" mark="edge" markrgb="0.2 0.3 0.4" />
    </asset>
    <worldbody>
        <light diffuse="0.5 0.5 0.5" pos="0 0 10" dir="0 0 -1" />
        <body name="_floor" pos="0 0 -0.144">
            <geom name="_floor.ground" type="plane" size="0 0 0.05" solimp="0.99 0.99 0.01"
                solref="0.02 1" material="grid" friction="1.0 0.005 0.0001" gap="0.0" />
        </body>
        <include file="$PATH_IS_REPLACED_WHEN_MODEL_IS_LOADED$/mjcf_template/body/eur-pallet.xml" />
        <body name="box" pos="0.6 0.4 0.055">
            <freejoint />
            <geom name="_box.geom" type="box" size="0.05 0.05 0.05" mass="1"
                rgba="0.9 0.1 0.1 1"
                solimp=".99 .99 .01" solref=".001 1" />
        </body>
        <body name="another_box" pos="2.0 2.0 -0.094">
            <freejoint />
            <geom name="_another_box.geom" type="box" size="0.05 0.05 0.05" mass="1"
                rgba="0.3 0.7 0.5 1"
                solimp=".99 .99 .01" solref=".001 1" />
        </body>
    </worldbody>
</mujoco>
"""

_TELEPORTS = [
    Teleport(name="another_box", target_position=(0.6, 0.4, 0.155), initial_position=(2.0, 2.0, -0.094)),
]

if __name__ == "__main__":
    from pet_physics.data_model.evaluation.stability_check import StabilityCheck
    from pet_physics.data_model.evaluation.stability_check_configuration import StabilityCheckConfiguration
    from pet_physics.plotting.chart_renderer import ChartRenderer
    from pet_physics.simulation import load_mujoco_model_from_string
    from pet_physics.simulation.callbacks.recorder_callback import RecorderCallback
    from pet_physics.simulation.callbacks.viewer_callback import ViewerCallback
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore
    from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities
    from pet_physics.simulation.physical_quantities.quantity_names import QuantityName
    from pet_physics.simulation.physical_quantities.recorders.force_penetration_recorder import ForcePenetrationRecorder
    from pet_physics.utils.logging_setup import setup_logging

    setup_logging("info")
    mj_model = load_mujoco_model_from_string(MJ_MODEL)

    stability_check = StabilityCheck(
        check_type="one_by_one",
        check_configuration=StabilityCheckConfiguration(
            parameters={
                "total_simulation_time_seconds": 10,
                "box_size_reduction_absolute_mm": 0.1,
            },
        ),
    )

    collection_body_quantities = CollectionBodyQuantities()
    force_recorder_callback = RecorderCallback(
        recorder_class=ForcePenetrationRecorder,
        collection_body_quantities=collection_body_quantities,
    )
    callbacks = [ViewerCallback(), force_recorder_callback]

    pet_physics_core = PETPhysicsCore(
        model=mj_model,
        stability_check=stability_check,
        body_teleports=_TELEPORTS,
        total_simulation_time=stability_check.check_configuration.total_simulation_time_seconds,
        teleport_interval=3,
        callbacks=callbacks,
    )
    pet_physics_core.init_for_run(1 / 30)
    pet_physics_core.run()

    # Render the line chart for the distance to origin and tiltedness of the box
    chart_renderer = ChartRenderer(simulation_time=force_recorder_callback.simulation_time)
    fig = chart_renderer.line_chart_body_contact_forces(
        body_name="box", force_history=collection_body_quantities.get_quantity_history(QuantityName.FORCE)
    )
    fig.show()
