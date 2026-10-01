"""
IoT Sensor Node ORM Models — Deployable ESP32 nodes with readings.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean
)
from app.database import Base


class IoTNode(Base):
    __tablename__ = "iot_nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(50), unique=True, nullable=False)  # e.g., "node_01"
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)

    # Drop position (SLAM-localized at deployment time)
    deploy_x = Column(Float, nullable=True)
    deploy_y = Column(Float, nullable=True)
    deploy_z = Column(Float, nullable=True)
    floor_level = Column(Integer, default=0)

    # Status
    is_deployed = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    deployed_at = Column(DateTime, nullable=True)
    last_heartbeat = Column(DateTime, nullable=True)

    # Battery
    battery_voltage = Column(Float, default=3.7)
    battery_percent = Column(Float, default=100.0)
    estimated_hours_remaining = Column(Float, default=12.0)

    # Mesh network
    mesh_hop_count = Column(Integer, default=0)
    parent_node_id = Column(String(50), nullable=True)
    rssi_to_parent = Column(Float, default=-30.0)

    # Current readings
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    voc_index = Column(Float, nullable=True)
    co_ppm = Column(Float, nullable=True)
    vibration_g = Column(Float, nullable=True)
    motion_detected = Column(Boolean, default=False)

    # Hardware info
    firmware_version = Column(String(20), default="1.0.0")
    mac_address = Column(String(17), nullable=True)


class NodeReading(Base):
    """Time-series readings from deployed IoT nodes — hypertable candidate."""
    __tablename__ = "node_readings"

    id = Column(Integer, primary_key=True)
    node_id = Column(String(50), nullable=False, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    voc_index = Column(Float, nullable=True)
    co_ppm = Column(Float, nullable=True)
    vibration_rms_g = Column(Float, nullable=True)
    motion_detected = Column(Boolean, default=False)

    battery_voltage = Column(Float, nullable=True)
    rssi = Column(Float, nullable=True)
