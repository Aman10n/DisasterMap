"""Pydantic schemas for Robot endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class RobotCreate(BaseModel):
    robot_id: str
    name: str = ""


class RobotCommand(BaseModel):
    command_type: str  # velocity, nav_goal, drop_node, return_to_base, stop
    linear_x: float = 0.0
    linear_y: float = 0.0
    angular_z: float = 0.0
    goal_x: Optional[float] = None
    goal_y: Optional[float] = None
    data: dict = {}


class RobotOut(BaseModel):
    id: int
    robot_id: str
    name: str
    mission_id: Optional[int] = None
    is_online: bool
    mode: str
    pos_x: float
    pos_y: float
    pos_z: float
    orientation_yaw: float
    battery_percent: float
    battery_voltage: float
    linear_speed: float
    angular_speed: float
    map_coverage_m2: float
    loop_closures: int
    slam_quality: float
    radio_quality: float
    using_lora_fallback: bool
    cpu_temp: float
    gpu_temp: float
    ram_usage_percent: float
    sensors_status: Dict = {}
    last_heartbeat: datetime

    class Config:
        from_attributes = True


class RobotTelemetryOut(BaseModel):
    timestamp: datetime
    pos_x: float
    pos_y: float
    pos_z: float
    yaw: float
    linear_vel_x: float
    battery_voltage: float
    visibility_percent: Optional[float] = None
    uwb_x: Optional[float] = None
    uwb_y: Optional[float] = None
    uwb_z: Optional[float] = None

    class Config:
        from_attributes = True
