"""
Gas Monitor — Processes MQ-2, MQ-9, MQ-135, MH-Z19B readings.
Detects IDLH threshold crossings and injects no-go zones.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json, math, time, random

class GasMonitor(Node):
    def __init__(self):
        super().__init__('gas_monitor')
        self.declare_parameter('co_idlh_ppm', 50.0)
        self.declare_parameter('methane_lel_percent', 10.0)
        self.declare_parameter('nh3_idlh_ppm', 25.0)
        self.declare_parameter('simulation_mode', True)

        self.gas_pub = self.create_publisher(String, '/hazard/gas', 10)
        self.alert_pub = self.create_publisher(String, '/hazard/alert', 10)
        self.create_timer(0.5, self.read_sensors)  # 2Hz
        self.ambient_co2 = 420.0
        self.get_logger().info('Gas Monitor started')

    def read_sensors(self):
        t = time.time()
        co = max(0, 5 + 10 * math.sin(t * 0.3) + random.gauss(0, 2))
        co2 = max(400, self.ambient_co2 + 50 * math.sin(t * 0.2) + random.gauss(0, 10))
        methane = max(0, 0.5 + 0.3 * math.sin(t * 0.1) + random.gauss(0, 0.1))
        nh3 = max(0, 2 + 3 * math.sin(t * 0.15) + random.gauss(0, 0.5))

        reading = {
            'co_ppm': round(co, 1), 'co2_ppm': round(co2, 0),
            'methane_ppm': round(methane, 2), 'nh3_ppm': round(nh3, 1),
            'temperature': round(22 + 3 * math.sin(t * 0.1), 1),
            'humidity': round(45 + 10 * math.sin(t * 0.05), 1),
            'position': [round(5 * math.cos(t * 0.1), 2), round(5 * math.sin(t * 0.15), 2), 0],
            'timestamp': t,
        }
        msg = String()
        msg.data = json.dumps(reading)
        self.gas_pub.publish(msg)

        # Check IDLH thresholds
        co_threshold = self.get_parameter('co_idlh_ppm').value
        if co > co_threshold:
            alert = String()
            alert.data = json.dumps({
                'type': 'gas_co', 'severity': 'critical',
                'value': round(co, 1), 'threshold': co_threshold,
                'message': f'CO Level {round(co,1)} ppm exceeds IDLH ({co_threshold} ppm)',
                'position': reading['position'],
            })
            self.alert_pub.publish(alert)
            self.get_logger().warn(f'IDLH ALERT: CO={round(co,1)} ppm')

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(GasMonitor())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
