"""
MQTT Publisher — Sends commands from server to robots via MQTT.
"""

import json
import structlog
from typing import Optional
import paho.mqtt.client as mqtt

from app.config import get_settings
from app.mqtt.topics import Topics

logger = structlog.get_logger()
settings = get_settings()


class MQTTPublisher:
    """Publishes commands to robots via MQTT."""

    def __init__(self):
        self._client: Optional[mqtt.Client] = None

    def _ensure_connected(self):
        if self._client is None:
            self._client = mqtt.Client(client_id="disastermap-publisher")
            self._client.connect(
                settings.mqtt_broker_host,
                settings.mqtt_broker_port,
            )

    def send_velocity(self, robot_id: str, linear_x: float, linear_y: float, angular_z: float):
        """Send velocity command (from joystick)."""
        self._publish(
            Topics.for_robot(Topics.CMD_VELOCITY, robot_id),
            {"linear_x": linear_x, "linear_y": linear_y, "angular_z": angular_z},
        )

    def send_nav_goal(self, robot_id: str, x: float, y: float):
        """Send navigation goal (from click-to-go)."""
        self._publish(
            Topics.for_robot(Topics.CMD_NAV_GOAL, robot_id),
            {"goal_x": x, "goal_y": y},
        )

    def send_drop_node(self, robot_id: str, node_id: str):
        """Command robot to deploy an IoT sensor node."""
        self._publish(
            Topics.for_robot(Topics.CMD_DROP_NODE, robot_id),
            {"node_id": node_id},
        )

    def send_return_to_base(self, robot_id: str):
        """Command robot to return to base."""
        self._publish(
            Topics.for_robot(Topics.CMD_RETURN_BASE, robot_id),
            {"command": "return_to_base"},
        )

    def send_stop(self, robot_id: str):
        """Emergency stop."""
        self._publish(
            Topics.for_robot(Topics.CMD_STOP, robot_id),
            {"command": "stop"},
        )

    def send_parameter(self, robot_id: str, param_name: str, value: float):
        """Send real-time parameter update to robot."""
        self._publish(
            Topics.for_robot(Topics.CMD_PARAMETER, robot_id),
            {"parameter": param_name, "value": value},
        )

    def send_nogo_zone(self, robot_id: str, vertices: list):
        """Inject a no-go zone polygon into robot's costmap."""
        self._publish(
            Topics.for_robot(Topics.CMD_NOGO_ZONE, robot_id),
            {"vertices": vertices},
        )

    def send_arm_command(self, robot_id: str, joints: list = None, xyz: list = None):
        """Send arm control command."""
        cmd = {}
        if joints:
            cmd["joint_angles"] = joints
        if xyz:
            cmd["end_effector_xyz"] = xyz
        self._publish(Topics.for_robot(Topics.CMD_ARM, robot_id), cmd)

    def _publish(self, topic: str, data: dict):
        """Publish JSON payload to MQTT topic."""
        try:
            self._ensure_connected()
            payload = json.dumps(data)
            self._client.publish(topic, payload, qos=1)
            logger.debug("MQTT published", topic=topic)
        except Exception as e:
            logger.error("MQTT publish failed", topic=topic, error=str(e))


# Singleton instance
publisher = MQTTPublisher()
