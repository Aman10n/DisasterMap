"""
MQTT Consumer — Async listener for all robot telemetry and sensor data.
Processes incoming messages and routes to appropriate services.
"""

import json
import asyncio
import structlog
from typing import Optional

from app.config import get_settings
from app.mqtt.topics import Topics

logger = structlog.get_logger()
settings = get_settings()


class MQTTConsumer:
    """
    Async MQTT consumer that subscribes to all robot topics
    and routes data to services for processing.
    """

    def __init__(self):
        self.connected = False
        self._running = False
        self._client = None
        self._handlers = {}
        self._ws_broadcast_callback = None
        self._event_loop = None

    def set_broadcast_callback(self, callback):
        """Set WebSocket broadcast callback for real-time forwarding."""
        self._ws_broadcast_callback = callback

    async def start(self):
        """Start the MQTT consumer loop."""
        self._running = True
        self._event_loop = asyncio.get_running_loop()
        logger.info(
            "MQTT consumer starting",
            broker=settings.mqtt_broker_host,
            port=settings.mqtt_broker_port,
        )

        while self._running:
            try:
                await self._connect_and_listen()
            except Exception as e:
                logger.error("MQTT connection error", error=str(e))
                self.connected = False
                await asyncio.sleep(5)  # Retry after 5 seconds

    async def _connect_and_listen(self):
        """Connect to MQTT broker and listen for messages."""
        try:
            import paho.mqtt.client as mqtt

            self._client = mqtt.Client(
                client_id="disastermap-server",
                transport="tcp",
            )
            self._client.on_connect = self._on_connect
            self._client.on_message = self._on_message
            self._client.on_disconnect = self._on_disconnect

            self._client.connect(
                settings.mqtt_broker_host,
                settings.mqtt_broker_port,
                keepalive=60,
            )

            self._client.loop_start()
            self.connected = True
            logger.info("MQTT connected")

            # Keep alive until stopped
            while self._running:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error("MQTT connection failed", error=str(e))
            self.connected = False
            raise

    def _on_connect(self, client, userdata, flags, rc):
        """Subscribe to all relevant topics on connection."""
        if rc == 0:
            self.connected = True
            # Subscribe to all robot telemetry (wildcard)
            client.subscribe("robot/+/telemetry")
            client.subscribe("robot/+/pose")
            client.subscribe("robot/+/battery")
            client.subscribe("robot/+/heartbeat")
            client.subscribe("robot/+/status")

            # SLAM
            client.subscribe("robot/+/slam/#")

            # Perception
            client.subscribe("robot/+/perception/#")

            # Hazards
            client.subscribe("robot/+/hazard/#")

            # IoT nodes
            client.subscribe("node/+/reading")
            client.subscribe("node/+/heartbeat")

            # UWB
            client.subscribe("uwb/#")

            # LoRa
            client.subscribe("lora/+/state")

            logger.info("MQTT subscribed to all topics")
        else:
            logger.error("MQTT connection failed", rc=rc)

    def _on_message(self, client, userdata, msg):
        """Route incoming messages to appropriate handlers."""
        try:
            topic = msg.topic
            payload = msg.payload

            # Try JSON decode
            try:
                data = json.loads(payload)
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = {"raw": payload.hex()}

            # Forward to WebSocket clients for real-time dashboard
            if self._ws_broadcast_callback and self._event_loop:
                asyncio.run_coroutine_threadsafe(
                    self._ws_broadcast_callback({
                        "type": "mqtt",
                        "topic": topic,
                        "data": data,
                    }),
                    self._event_loop,
                )

            # Log (debug level for high-frequency topics)
            if "telemetry" not in topic and "pose" not in topic:
                logger.debug("MQTT message", topic=topic)

        except Exception as e:
            logger.error("MQTT message processing error", error=str(e))

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning("MQTT disconnected", rc=rc)

    def stop(self):
        """Stop the consumer."""
        self._running = False
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
        self.connected = False
        logger.info("MQTT consumer stopped")
