"""
Victim ORM Models — Quadruple sensor fusion with hypothesis tracking.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum, Text, JSON, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from app.database import Base


class DetectionModality(str, enum.Enum):
    THERMAL = "thermal"
    ACOUSTIC = "acoustic"
    CO2 = "co2"
    VISUAL = "visual"


class VictimStatus(str, enum.Enum):
    HYPOTHESIS = "hypothesis"
    CONFIRMED = "confirmed"
    RESCUED = "rescued"
    FALSE_POSITIVE = "false_positive"


class VictimHypothesis(Base):
    """
    Pending victim hypothesis maintained by the Kalman filter.
    Promoted to VictimRecord when 3+ modalities associate within 90s window.
    """
    __tablename__ = "victim_hypotheses"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)

    # Kalman state
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)
    pos_z = Column(Float, nullable=False)
    covariance_xx = Column(Float, default=1.0)
    covariance_yy = Column(Float, default=1.0)
    covariance_zz = Column(Float, default=1.0)

    # Modality flags
    thermal_detected = Column(Boolean, default=False)
    acoustic_detected = Column(Boolean, default=False)
    co2_detected = Column(Boolean, default=False)
    visual_detected = Column(Boolean, default=False)
    modality_count = Column(Integer, default=0)

    # Confidence
    confidence_score = Column(Float, default=0.0)
    first_detection_at = Column(DateTime, default=datetime.utcnow)
    last_detection_at = Column(DateTime, default=datetime.utcnow)
    window_expires_at = Column(DateTime, nullable=True)  # 90-second window

    # Status
    status = Column(Enum(VictimStatus), default=VictimStatus.HYPOTHESIS)
    promoted_to_record_id = Column(Integer, nullable=True)

    detections = relationship("DetectionEvent", back_populates="hypothesis", cascade="all, delete-orphan")


class VictimRecord(Base):
    """
    Confirmed victim record — displayed on the dashboard victim board.
    """
    __tablename__ = "victim_records"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    hypothesis_id = Column(Integer, ForeignKey("victim_hypotheses.id"), nullable=True)

    # 3D position in global map frame
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)
    pos_z = Column(Float, nullable=False)
    floor_level = Column(Integer, default=0)

    # Detection info
    confirmed_at = Column(DateTime, default=datetime.utcnow)
    modalities_triggered = Column(JSON, default=list)  # ["thermal", "acoustic", "visual"]
    confidence_score = Column(Float, default=0.0)

    # Evidence
    thermal_image_path = Column(String(500), nullable=True)
    visual_image_path = Column(String(500), nullable=True)
    audio_clip_path = Column(String(500), nullable=True)
    co2_trace_data = Column(JSON, nullable=True)

    # Pose estimation
    pose_keypoints = Column(JSON, nullable=True)  # YOLOv8-Pose output
    body_visible_parts = Column(JSON, nullable=True)  # ["head", "shoulders", ...]
    estimated_burial_depth = Column(String(50), nullable=True)  # surface, partial, deep

    # Rescue status
    status = Column(Enum(VictimStatus), default=VictimStatus.CONFIRMED)
    rescue_notes = Column(Text, default="")
    rescued_at = Column(DateTime, nullable=True)


class DetectionEvent(Base):
    """
    Individual detection from a single modality — associated with a hypothesis.
    """
    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True)
    hypothesis_id = Column(Integer, ForeignKey("victim_hypotheses.id"), nullable=False)
    robot_id = Column(String(50), nullable=False)

    modality = Column(Enum(DetectionModality), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Detection position
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)
    pos_z = Column(Float, nullable=False)

    # Modality-specific
    confidence = Column(Float, default=0.0)
    raw_value = Column(Float, nullable=True)  # e.g., temperature, CO2 ppm, audio dB
    sensor_data = Column(JSON, nullable=True)  # Raw sensor payload
    evidence_path = Column(String(500), nullable=True)  # Path to evidence file

    hypothesis = relationship("VictimHypothesis", back_populates="detections")
