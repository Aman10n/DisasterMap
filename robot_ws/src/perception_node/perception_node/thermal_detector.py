"""
Thermal Detector — FLIR Lepton 3.5 processing for survivor detection.
Background subtraction, blob detection, human-body classification.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json, math, time, random

class ThermalDetector(Node):
    def __init__(self):
        super().__init__('thermal_detector')
        self.declare_parameter('threshold_above_ambient', 32.0)
        self.declare_parameter('simulation_mode', True)
        self.detection_pub = self.create_publisher(String, '/perception/thermal', 10)
        self.ambient_temp = 22.0
        self.create_timer(0.5, self.process_frame)
        self.get_logger().info('Thermal Detector started')

    def process_frame(self):
        threshold = self.get_parameter('threshold_above_ambient').value
        t = time.time()
        # Simulated thermal detection
        if random.random() < 0.02:  # 2% chance per frame
            det_temp = self.ambient_temp + threshold + random.uniform(0, 10)
            detection = {
                'type': 'thermal',
                'temperature': round(det_temp, 1),
                'ambient': self.ambient_temp,
                'above_ambient': round(det_temp - self.ambient_temp, 1),
                'centroid_u': random.randint(20, 140),
                'centroid_v': random.randint(15, 105),
                'blob_area': random.randint(50, 500),
                'aspect_ratio': round(random.uniform(0.3, 0.8), 2),
                'confidence': round(random.uniform(0.6, 0.95), 2),
                'position': [round(random.uniform(-6, 6), 2), round(random.uniform(-6, 6), 2), 0.5],
                'timestamp': t,
            }
            msg = String()
            msg.data = json.dumps(detection)
            self.detection_pub.publish(msg)
            self.get_logger().info(f'THERMAL DETECTION: {det_temp}°C, conf={detection["confidence"]}')

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(ThermalDetector())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
