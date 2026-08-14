"""Chart renderer for quantities recorded during a MuJoCo simulation.

This module contains a class that is used to create charts of quantities that were recorded during a MuJoCo simulation.
"""

import plotly.graph_objects as go

from pet_physics.data_model.physical_quantities.acceleration import Acceleration
from pet_physics.data_model.physical_quantities.body_forces import BodyForces
from pet_physics.data_model.physical_quantities.pose import Pose
from pet_physics.data_model.physical_quantities.simulation_time import SimulationTime
from pet_physics.plotting.plotting_utils import AxisInfo, create_interactive_line_chart
from pet_physics.simulation.physical_quantities.history.acceleration_history import AccelerationHistory
from pet_physics.simulation.physical_quantities.history.force_history import ForceHistory
from pet_physics.simulation.physical_quantities.history.pose_history import PoseHistory


class ChartRenderer:
    """Creates charts based on quantities recorded during a MuJoCo simulation."""

    def __init__(self, simulation_time: SimulationTime) -> None:
        """The constructor.

        Args:
            simulation_time: The recorded simulation time in every simulation step.
        """
        self._simulation_time = simulation_time
        """The recorded simulation time in every simulation step."""

    def line_chart_body_contact_forces(self, body_name: str, force_history: ForceHistory) -> go.Figure:
        """Creates a line chart that has two y-axes. On the first, the contact forces at the bottom of the body
        are displayed. The secondary y-axis contains the contact forces that act on top of the body. Both share the
        simulation time on the x-axis.

        Args:
            body_name: The name of the body whose contact forces are visualized.
            force_history: The history of the forces that were recorded during the simulation.

        Returns:
            The created line chart.
        """
        body_forces: list[BodyForces] = force_history.get_values_of_body(body_name)

        simulation_time_values = self._simulation_time.values

        # use total z-component of all contact forces so non-vertical contacts are included
        body_contact_forces_bottom = [force.sum_contact_forces_z for force in body_forces]
        body_contact_forces_top = [force.sum_contact_forces_z_top for force in body_forces]

        x_axis = AxisInfo(name="simulation_time", values=simulation_time_values, label="Simulation time (seconds)")
        y1_axis = AxisInfo(
            name="contact_forces_bottom", values=body_contact_forces_bottom, label="Contact Forces at Bottom (Newton)"
        )
        y2_axis = AxisInfo(
            name="contact_forces_top", values=body_contact_forces_top, label="Contact Forces on Top (Newton)"
        )
        fig = create_interactive_line_chart(
            x_axis=x_axis,
            y1_axis=y1_axis,
            y2_axis=y2_axis,
            title=f"'{body_name}' - body specific quantities",
        )

        return fig

    def line_chart_body_top_contact_forces_and_acceleration(
        self, body_name: str, force_history: ForceHistory, acceleration_history: AccelerationHistory
    ) -> go.Figure:
        """Creates a line chart that has two y-axes. On the first, the contact forces on top of the body are displayed.
        The secondary y-axis contains the norm of the linear acceleration of this body. Both share the simulation time
        on the x-axis.

        Args:
            body_name: The name of the body whose contact forces are visualized.
            force_history: The history of the forces that were recorded during the simulation.
            acceleration_history: The history of the accelerations that were recorded during the simulation.

        Returns:
            The created line chart.
        """

        force_history_of_body: list[BodyForces] = force_history.get_values_of_body(body_name)
        acceleration_history_of_body: list[Acceleration] = acceleration_history.get_values_of_body(body_name)

        simulation_time_values = self._simulation_time.values

        body_contact_forces_top = [force.sum_contact_forces_z_top for force in force_history_of_body]

        body_linear_acceleration = [
            acceleration_i.norm_linear_acceleration for acceleration_i in acceleration_history_of_body
        ]

        x_axis = AxisInfo(name="simulation_time", values=simulation_time_values, label="Simulation time (seconds)")
        y1_axis = AxisInfo(
            name="contact_forces_top", values=body_contact_forces_top, label="Contact Forces on Top (Newton)"
        )
        y2_axis = AxisInfo(
            name="norm_linear_acceleration",
            values=body_linear_acceleration,
            label="Linear Acceleration of the Body (meter/s^2)",
        )
        fig = create_interactive_line_chart(
            x_axis=x_axis,
            y1_axis=y1_axis,
            y2_axis=y2_axis,
            title=f"'{body_name}' - body specific quantities",
        )

        return fig

    def line_chart_body_distance_to_origin_and_tiltedness_wrt_z_axis(
        self, body_name: str, pose_history: PoseHistory
    ) -> go.Figure:
        """Creates a line chart showing distance to origin and tiltedness wrt. the z-axis.

        The chart has two y-axes. On the first, the distance of the body to the origin
        is displayed. The secondary y-axis contains the tiltedness of the body wrt. to
        the z-axis. Both share the simulation time on the x-axis.

        Args:
            body_name: The name of the body whose pose is visualized.
            pose_history: The history of the poses recorded during the simulation.

        Returns:
            The created line chart.
        """
        pose_history_of_body: list[Pose] = pose_history.get_values_of_body(body_name)

        simulation_time_values = self._simulation_time.values

        body_distance_to_origin = [pose.distance_to_origin for pose in pose_history_of_body]
        body_tiltedness_wrt_z_axis = [pose.angle_with_z_axis for pose in pose_history_of_body]

        x_axis = AxisInfo(name="simulation_time", values=simulation_time_values, label="Simulation time (seconds)")
        y1_axis = AxisInfo(
            name="distance_to_origin", values=body_distance_to_origin, label="Distance of Body to Origin (meters)"
        )
        y2_axis = AxisInfo(
            name="tiltedness_wrt_direction_z_axis",
            values=body_tiltedness_wrt_z_axis,
            label="Tiltedness of Body (angle normal box with normal z-axis (Degrees)",
        )
        fig = create_interactive_line_chart(
            x_axis=x_axis,
            y1_axis=y1_axis,
            y2_axis=y2_axis,
            title=f"'{body_name}' - body specific quantities",
        )

        return fig
