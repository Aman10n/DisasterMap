"""
Robot ORM Models — Fleet management with telemetry hypertable.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


class Robot(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(String(50), unique=True, nullable=False)  # e.g., "robot1"
    name = Column(String(255), default="")
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)

    # Current state
    is_online = Column(Boolean, default=False)
    mode = Column(String(50), default="idle")  # idle, exploring, manual, returning, hazard_response

    # Position (SLAM-estimated)
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)
    pos_z = Column(Float, default=0.0)
    orientation_yaw = Column(Float, default=0.0)

    # Battery
    battery_voltage = Column(Float, default=0.0)
    battery_percent = Column(Float, default=100.0)

    # Navigation
    current_goal_x = Column(Float, nullable=True)
    current_goal_y = Column(Float, nullable=True)
    linear_speed = Column(Float, default=0.0)
    angular_speed = Column(Float, default=0.0)

    # SLAM stats
    map_coverage_m2 = Column(Float, default=0.0)
    loop_closures = Column(Integer, default=0)
    slam_quality = Column(Float, default=1.0)  # 0.0-1.0

    # Radio
    radio_rssi = Column(Float, default=-30.0)  # dBm
    radio_quality = Column(Float, default=1.0)  # 0.0-1.0
    using_lora_fallback = Column(Boolean, default=False)

    # Hardware
    cpu_temp = Column(Float, default=0.0)
    gpu_temp = Column(Float, default=0.0)
    ram_usage_percent = Column(Float, default=0.0)

    # Sensors active
    sensors_status = Column(JSON, default=dict)  # {"lidar": true, "rgbd": true, ...}

    last_heartbeat = Column(DateTime, default=datetime.utcnow)

    # Relationships
    mission = relationship("Mission", back_populates="robots")


class RobotTelemetry(Base):
    """
    High-frequency telemetry — stored as TimescaleDB hypertable.
    Published at 10Hz, stored for post-mission analysis.
    """
    __tablename__ = "robot_telemetry"

    id = Column(Integer, primary_key=True)
    robot_id = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Pose
    pos_x = Column(Float)
    pos_y = Column(Float)
    pos_z = Column(Float)
    roll = Column(Float)
    pitch = Column(Float)
    yaw = Column(Float)

    # Velocity
    linear_vel_x = Column(Float)
    linear_vel_y = Column(Float)
    angular_vel_z = Column(Float)

    # Battery
    battery_voltage = Column(Float)
    battery_current = Column(Float)

    # IMU
    imu_accel_x = Column(Float)
    imu_accel_y = Column(Float)
    imu_accel_z = Column(Float)

    # Visibility
    visibility_percent = Column(Float)

    # UWB position (independent of SLAM)
    uwb_x = Column(Float, nullable=True)
    uwb_y = Column(Float, nullable=True)
    uwb_z = Column(Float, nullable=True)
