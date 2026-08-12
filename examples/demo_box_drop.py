"""A script that demonstrates the evaluator box drop. Note that it does not work for bodies that are teleported.

The model puts a cube on the edge of the pallet which will drop due to gravity at timestamp 33.
"""

# TODO(florian): Add this as test for the box drop detection.

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
        <body name="_pallet" pos="0.6 0.4 -0.072">
            <geom name="_pallet.top.component.wide.1" type="box" size="0.6 0.075 0.015" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 -0.325 0.062" />
            <geom name="_pallet.top.component.wide.2" type="box" size="0.6 0.075 0.015" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 0 0.062" />
            <geom name="_pallet.top.component.wide.3" type="box" size="0.6 0.075 0.015" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 0.325 0.062" />

            <geom name="_pallet.top.component.narrow.1" type="box" size="0.6 0.06 0.015" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 0.1625 0.062" />
            <geom name="_pallet.top.component.narrow.2" type="box" size="0.6 0.06 0.015" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 -0.1625 0.062" />

            <geom name="_pallet.middle.fillet.1" type="box" size="0.075 0.4 0.007" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 0 0.044" />
            <geom name="_pallet.middle.fillet.2" type="box" size="0.075 0.4 0.007" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="-0.525 0 0.044" />
            <geom name="_pallet.middle.fillet.3" type="box" size="0.075 0.4 0.007" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0.525 0 0.044" />

            <!-- front row-->
            <geom name="_pallet.middle.cuboid.1" type="box" size="0.068 0.058 0.0445" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="-0.532 -0.342 -0.0075" />
            <geom name="_pallet.middle.cuboid.2" type="box" size="0.068 0.058 0.0445" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 -0.342 -0.0075" />
            <geom name="_pallet.middle.cuboid.3" type="box" size="0.068 0.058 0.0445" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0.532 -0.342 -0.0075" />
            <!-- middle row-->
            <geom name="_pallet.middle.cuboid.4" type="box" size="0.068 0.058 0.0445" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="-0.532 0 -0.0075" />
            <geom name="_pallet.middle.cuboid.5" type="box" size="0.068 0.058 0.0445" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 0 -0.0075" />
            <geom name="_pallet.middle.cuboid.6" type="box" size="0.068 0.058 0.0445" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0.532 0 -0.0075" />
            <!-- back row-->
            <geom name="_pallet.middle.cuboid.7" type="box" size="0.068 0.058 0.0445" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="-0.532 0.342 -0.0075" />
            <geom name="_pallet.middle.cuboid.8" type="box" size="0.068 0.058 0.0445" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 0.342 -0.0075" />
            <geom name="_pallet.middle.cuboid.9" type="box" size="0.068 0.058 0.0445" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0.532 0.342 -0.0075" />

            <geom name="_pallet.bottom.bottom.1" type="box" size="0.6 0.058 0.01" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 -0.342 -0.062" />
            <geom name="_pallet.bottom.bottom.2" type="box" size="0.6 0.058 0.01" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 0 -0.062" />
            <geom name="_pallet.bottom.bottom.3" type="box" size="0.6 0.058 0.01" mass="2"
                rgba="0.871 0.722 0.529 1"
                solimp=".99 .99 .01" solref=".001 1" pos="0 0.342 -0.062" />
        </body>
        <body name="box" pos="1.2 0.4 0.055">
            <freejoint />
            <geom name="_box.geom" type="box" size="0.05 0.05 0.05" mass="1"
                rgba="0.9 0.1 0.1 1"
                solimp=".99 .99 .01" solref=".001 1" />
        </body>
    </worldbody>
</mujoco>
"""

if __name__ == "__main__":
    from pet_physics.data_model.evaluation.stability_check import StabilityCheck
    from pet_physics.data_model.evaluation.stability_check_configuration import StabilityCheckConfiguration
    from pet_physics.evaluation.pose.evaluator_box_drop import EvaluatorBoxDrop
    from pet_physics.simulation import load_mujoco_model_from_string
    from pet_physics.simulation.callbacks.recorder_callback import RecorderCallback
    from pet_physics.simulation.callbacks.viewer_callback import ViewerCallback
    from pet_physics.simulation.pet_physics_core import PETPhysicsCore
    from pet_physics.simulation.physical_quantities.collection_body_quantities import CollectionBodyQuantities
    from pet_physics.simulation.physical_quantities.recorders.pose_recorder import PoseRecorder

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
    pose_recorder_callback = RecorderCallback(
        recorder_class=PoseRecorder,
        collection_body_quantities=collection_body_quantities,
    )

    pet_physics_core = PETPhysicsCore(
        model=mj_model,
        stability_check=stability_check,
        body_teleports=[],
        total_simulation_time=stability_check.check_configuration.total_simulation_time_seconds,
        teleport_interval=3,
        callbacks=[
            ViewerCallback(),
            pose_recorder_callback,
        ],
    )
    pet_physics_core.init_for_run(1 / 30)
    pet_physics_core.run()

    # Evaluate box drop
    evaluator_box_drop = EvaluatorBoxDrop(
        body_name_to_size_mapping={
            "box": (0.05, 0.05, 0.05),
        }
    )
    result_evaluator_box_drop = evaluator_box_drop.evaluate(collection_body_quantities)
    # Should print that box dropped at timestamp 33.
    print(result_evaluator_box_drop.to_dict())
