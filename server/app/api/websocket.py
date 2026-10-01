"""WebSocket Hub — Real-time data streaming to all dashboard clients."""

import asyncio
import json
import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set

from app.config import get_settings

logger = structlog.get_logger()
router = APIRouter()
settings = get_settings()

# Connected WebSocket clients
connected_clients: Set[WebSocket] = set()


async def broadcast(message: dict):
    """Broadcast a message to all connected WebSocket clients."""
    if not connected_clients:
        return
    data = json.dumps(message)
    disconnected = set()
    for ws in connected_clients:
        try:
            await ws.send_text(data)
        except Exception:
            disconnected.add(ws)
    connected_clients.difference_update(disconnected)


@router.websocket("/live")
async def websocket_live(ws: WebSocket):
    """
    Main WebSocket endpoint for real-time dashboard data.
    Streams: robot telemetry, SLAM updates, detections, alerts.
    """
    await ws.accept()
    connected_clients.add(ws)
    logger.info("WebSocket client connected", total=len(connected_clients))
    sim_task = None

    try:
        # Send initial state
        await ws.send_json({
            "type": "connection",
            "status": "connected",
            "message": "DisasterMap real-time stream active",
        })

        # Keep demo telemetry available during development without mixing it
        # into production MQTT streams.
        if settings.debug:
            sim_task = asyncio.create_task(_simulation_stream(ws))

        # Listen for incoming messages (commands from dashboard)
        while True:
            try:
                data = await ws.receive_text()
                msg = json.loads(data)
                await _handle_client_message(ws, msg)
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        pass
    finally:
        if sim_task:
            sim_task.cancel()
        connected_clients.discard(ws)
        logger.info("WebSocket client disconnected", total=len(connected_clients))


async def _simulation_stream(ws: WebSocket):
    """Stream simulated robot data for demo/testing."""
    import math
    import random
    t = 0.0

    try:
        while True:
            # Simulate robot moving in a search pattern
            x = 5.0 * math.cos(t * 0.1) + random.gauss(0, 0.05)
            y = 5.0 * math.sin(t * 0.15) + random.gauss(0, 0.05)
            yaw = math.atan2(math.cos(t * 0.15) * 0.15, -math.sin(t * 0.1) * 0.1)

            await ws.send_json({
                "type": "robot_pose",
                "robot_id": "robot1",
                "data": {
                    "x": round(x, 3),
                    "y": round(y, 3),
                    "z": 0.0,
                    "yaw": round(yaw, 3),
                    "battery": max(100 - t * 0.5, 10),
                    "speed": round(0.3 + 0.1 * math.sin(t), 2),
                }
            })

            # Simulated sensor readings
            await ws.send_json({
                "type": "sensor_data",
                "robot_id": "robot1",
                "data": {
                    "co_ppm": round(max(0, 5 + 10 * math.sin(t * 0.3) + random.gauss(0, 2)), 1),
                    "co2_ppm": round(max(400, 450 + 50 * math.sin(t * 0.2) + random.gauss(0, 10)), 0),
                    "temperature": round(22 + 3 * math.sin(t * 0.1) + random.gauss(0, 0.5), 1),
                    "humidity": round(45 + 10 * math.sin(t * 0.05), 1),
                    "visibility": round(max(20, min(100, 85 - 15 * math.sin(t * 0.08))), 0),
                }
            })

            t += 0.5
            await asyncio.sleep(0.5)

    except (WebSocketDisconnect, asyncio.CancelledError):
        pass


async def _handle_client_message(ws: WebSocket, msg: dict):
    """Handle incoming messages from dashboard clients."""
    msg_type = msg.get("type", "")

    if msg_type == "subscribe":
        # Client wants to subscribe to specific data types
        logger.debug("Client subscription", topics=msg.get("topics", []))

    elif msg_type == "command":
        # Forward command to MQTT
        logger.info("Dashboard command received", command=msg)

    await ws.send_json({"type": "ack", "original_type": msg_type})
