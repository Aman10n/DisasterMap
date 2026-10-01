"""Pydantic schemas for Mission endpoints."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.mission import MissionState


class MissionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    location_name: str = ""
    building_type: str = ""


class MissionTransition(BaseModel):
    target_state: MissionState
    reason: str = ""
    operator_override: bool = False


class MissionEventOut(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    severity: str
    title: str
    description: str
    data: dict = {}
    from_state: Optional[str] = None
    to_state: Optional[str] = None
    robot_x: Optional[float] = None
    robot_y: Optional[float] = None
    robot_z: Optional[float] = None

    class Config:
        from_attributes = True


class MissionOut(BaseModel):
    id: int
    name: str
    description: str
    state: MissionState
    location_name: str
    building_type: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    area_explored_m2: float
    victims_confirmed: int
    hazards_detected: int
    exploration_rate_m2_min: float
    rosbag_path: Optional[str] = None
    report_path: Optional[str] = None

    class Config:
        from_attributes = True


class MissionSummary(BaseModel):
    id: int
    name: str
    state: MissionState
    location_name: str
    created_at: datetime
    area_explored_m2: float
    victims_confirmed: int
    hazards_detected: int

    class Config:
        from_attributes = True
