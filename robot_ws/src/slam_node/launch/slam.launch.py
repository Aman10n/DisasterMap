"""SLAM launch file — starts RTAB-Map, robot_localization EKF, and OctoMap server."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    sim_mode = LaunchConfiguration('simulation_mode', default='true')

    return LaunchDescription([
        DeclareLaunchArgument('simulation_mode', default_value='true',
            description='Run in simulation mode with synthetic data'),

        # SLAM Manager
        Node(
            package='slam_node',
            executable='slam_manager',
            name='slam_manager',
            output='screen',
            parameters=[{
                'simulation_mode': sim_mode,
                'octomap_resolution': 0.05,
                'loop_closure_threshold': 0.11,
                'map_update_rate': 2.0,
            }],
        ),

        # Robot Localization EKF (fuses IMU + odom + UWB)
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter',
            output='screen',
            parameters=['config/robot_localization.yaml'],
            condition=None,  # Always run, uses sim data in sim mode
        ),
    ])
