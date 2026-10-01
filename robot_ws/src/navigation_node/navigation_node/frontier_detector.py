"""
Frontier Detector — Detects and clusters frontier cells from occupancy grid.
Publishes exploration goals for Nav2.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import json, math, time, random


class FrontierDetector(Node):
    def __init__(self):
        super().__init__('frontier_detector')
        self.declare_parameter('simulation_mode', True)
        self.declare_parameter('w_distance', 1.0)
        self.declare_parameter('w_size', 0.5)
        self.declare_parameter('w_hazard', 0.3)

        self.goal_pub = self.create_publisher(PoseStamped, '/exploration/goal', 10)
        self.frontier_pub = self.create_publisher(String, '/exploration/frontiers', 10)
        self.create_timer(1.0, self.detect_frontiers)  # 1Hz

        self.robot_pos = [0.0, 0.0]
        self.create_subscription(PoseStamped, '/slam/pose', self.pose_callback, 10)
        self.get_logger().info('Frontier Detector started')

    def pose_callback(self, msg):
        self.robot_pos = [msg.pose.position.x, msg.pose.position.y]

    def detect_frontiers(self):
        t = time.time()
        w_d = self.get_parameter('w_distance').value
        w_s = self.get_parameter('w_size').value

        # Simulated frontier clusters
        clusters = [
            {'centroid': [random.uniform(-8, 8), random.uniform(-8, 8)], 'size': random.randint(5, 30)}
            for _ in range(random.randint(3, 8))
        ]

        # Score each cluster
        best_goal = None
        best_utility = -float('inf')
        for c in clusters:
            dist = math.sqrt((self.robot_pos[0]-c['centroid'][0])**2 + (self.robot_pos[1]-c['centroid'][1])**2)
            utility = w_d * (1.0/max(dist, 0.5)) + w_s * math.log1p(c['size'])
            c['utility'] = round(utility, 3)
            if utility > best_utility:
                best_utility = utility
                best_goal = c['centroid']

        # Publish frontiers info
        info = String()
        info.data = json.dumps({'clusters': len(clusters), 'best_utility': round(best_utility, 3)})
        self.frontier_pub.publish(info)

        # Publish goal
        if best_goal:
            goal = PoseStamped()
            goal.header.stamp = self.get_clock().now().to_msg()
            goal.header.frame_id = 'map'
            goal.pose.position.x = best_goal[0]
            goal.pose.position.y = best_goal[1]
            self.goal_pub.publish(goal)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(FrontierDetector())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
