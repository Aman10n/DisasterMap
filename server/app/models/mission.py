"""
Mission ORM Models — 9-state FSM with event logging.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum, Text, JSON, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base


class MissionState(str, enum.Enum):
    IDLE = "IDLE"
    PRECHECK = "PRECHECK"
    DEPLOYED = "DEPLOYED"
    EXPLORING = "EXPLORING"
    HAZARD_RESPONSE = "HAZARD_RESPONSE"
    VICTIM_CONFIRMED = "VICTIM_CONFIRMED"
    MANUAL_OVERRIDE = "MANUAL_OVERRIDE"
    RETURN_TO_BASE = "RETURN_TO_BASE"
    MISSION_COMPLETE = "MISSION_COMPLETE"


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    state = Column(Enum(MissionState), default=MissionState.IDLE, nullable=False)

    # Location metadata
    location_name = Column(String(255), default="")
    building_type = Column(String(100), default="")  # collapsed, underground, industrial

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Stats (updated live)
    area_explored_m2 = Column(Float, default=0.0)
    victims_confirmed = Column(Integer, default=0)
    hazards_detected = Column(Integer, default=0)
    exploration_rate_m2_min = Column(Float, default=0.0)

    # Rosbag
    rosbag_path = Column(String(500), nullable=True)
    report_path = Column(String(500), nullable=True)

    # Relationships
    events = relationship("MissionEvent", back_populates="mission", cascade="all, delete-orphan")
    robots = relationship("Robot", back_populates="mission")


class MissionEvent(Base):
    __tablename__ = "mission_events"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    event_type = Column(String(50), nullable=False)  # state_change, alert, detection, slam_loop_closure, etc.
    severity = Column(String(20), default="info")  # info, warning, critical
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    data = Column(JSON, default=dict)  # Arbitrary event data

    # For state transitions
    from_state = Column(String(50), nullable=True)
    to_state = Column(String(50), nullable=True)
    operator_acknowledged = Column(Boolean, default=False)

    # Spatial context
    robot_x = Column(Float, nullable=True)
    robot_y = Column(Float, nullable=True)
    robot_z = Column(Float, nullable=True)

    mission = relationship("Mission", back_populates="events")
