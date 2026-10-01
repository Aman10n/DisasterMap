"""Pydantic schemas for Victim endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class VictimRecordOut(BaseModel):
    id: int
    mission_id: int
    pos_x: float
    pos_y: float
    pos_z: float
    floor_level: int
    confirmed_at: datetime
    modalities_triggered: List[str] = []
    confidence_score: float
    thermal_image_path: Optional[str] = None
    visual_image_path: Optional[str] = None
    audio_clip_path: Optional[str] = None
    co2_trace_data: Optional[dict] = None
    pose_keypoints: Optional[dict] = None
    body_visible_parts: Optional[list] = None
    estimated_burial_depth: Optional[str] = None
    status: str
    rescue_notes: str = ""

    class Config:
        from_attributes = True


class VictimHypothesisOut(BaseModel):
    id: int
    mission_id: int
    pos_x: float
    pos_y: float
    pos_z: float
    modality_count: int
    thermal_detected: bool
    acoustic_detected: bool
    co2_detected: bool
    visual_detected: bool
    confidence_score: float
    status: str
    first_detection_at: datetime
    last_detection_at: datetime

    class Config:
        from_attributes = True


class VictimStatusUpdate(BaseModel):
    status: str  # rescued, false_positive
    rescue_notes: str = ""
