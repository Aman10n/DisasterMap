"""
SLAM Manager Node — Orchestrates RTAB-Map, EKF fusion, and OctoMap publishing.
Includes simulation mode for testing without hardware.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from sensor_msgs.msg import PointCloud2, Imu
from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Odometry
import json
import math
import time


class SLAMManager(Node):
    def __init__(self):
        super().__init__('slam_manager')

        # Parameters
        self.declare_parameter('simulation_mode', True)
        self.declare_parameter('octomap_resolution', 0.05)
        self.declare_parameter('loop_closure_threshold', 0.11)
        self.declare_parameter('map_update_rate', 2.0)

        self.sim_mode = self.get_parameter('simulation_mode').value
        self.resolution = self.get_parameter('octomap_resolution').value

        # Publishers
        self.pose_pub = self.create_publisher(PoseStamped, '/slam/pose', 10)
        self.quality_pub = self.create_publisher(Float32, '/slam/quality', 10)
        self.octomap_pub = self.create_publisher(String, '/slam/octomap_diff', 10)
        self.loop_closure_pub = self.create_publisher(String, '/slam/loop_closure', 10)

        # Subscribers (from real sensors)
        if not self.sim_mode:
            self.create_subscription(PointCloud2, '/velodyne_points', self.lidar_callback, 10)
            self.create_subscription(Imu, '/imu/data', self.imu_callback, 10)
            self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # State
        self.position = [0.0, 0.0, 0.0]
        self.orientation_yaw = 0.0
        self.slam_quality = 1.0
        self.loop_closure_count = 0
        self.voxel_count = 0
        self.start_time = time.time()

        # Timers
        rate = self.get_parameter('map_update_rate').value
        self.create_timer(1.0 / rate, self.publish_map_update)

        if self.sim_mode:
            self.create_timer(0.1, self.simulation_tick)  # 10Hz sim

        self.get_logger().info(f'SLAM Manager started (simulation={self.sim_mode})')

    def simulation_tick(self):
        """Generate simulated robot motion and SLAM data."""
        t = time.time() - self.start_time

        # Simulated search pattern
        self.position[0] = 5.0 * math.cos(t * 0.1)
        self.position[1] = 5.0 * math.sin(t * 0.15)
        self.position[2] = 0.0
        self.orientation_yaw = math.atan2(
            math.cos(t * 0.15) * 0.15,
            -math.sin(t * 0.1) * 0.1
        )

        # Simulated quality degradation and recovery
        self.slam_quality = 0.85 + 0.15 * math.sin(t * 0.05)

        # Publish pose
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'map'
        pose.pose.position.x = self.position[0]
        pose.pose.position.y = self.position[1]
        pose.pose.position.z = self.position[2]
        self.pose_pub.publish(pose)

        # Publish quality
        quality_msg = Float32()
        quality_msg.data = self.slam_quality
        self.quality_pub.publish(quality_msg)

        # Simulated loop closure events
        if t > 30 and int(t) % 60 == 0 and self.loop_closure_count < int(t / 60):
            self.loop_closure_count += 1
            lc_msg = String()
            lc_msg.data = json.dumps({
                'count': self.loop_closure_count,
                'drift_before': round(0.1 + 0.05 * self.loop_closure_count, 3),
                'drift_after': round(0.02 + 0.01 * self.loop_closure_count, 3),
                'timestamp': t,
            })
            self.loop_closure_pub.publish(lc_msg)
            self.get_logger().info(f'Loop closure #{self.loop_closure_count}')

    def publish_map_update(self):
        """Publish OctoMap diff (simulated voxel updates)."""
        self.voxel_count += 10
        diff_msg = String()
        diff_msg.data = json.dumps({
            'voxel_count': self.voxel_count,
            'resolution': self.resolution,
            'robot_position': self.position,
        })
        self.octomap_pub.publish(diff_msg)

    def lidar_callback(self, msg):
        """Process LiDAR point cloud for ICP scan matching."""
        self.get_logger().debug('LiDAR scan received')

    def imu_callback(self, msg):
        """Process IMU for EKF pre-integration."""
        pass

    def odom_callback(self, msg):
        """Process wheel odometry."""
        pass


def main(args=None):
    rclpy.init(args=args)
    node = SLAMManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
