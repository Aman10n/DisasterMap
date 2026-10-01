"""Pydantic schemas for Sensor (IoT Node) endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IoTNodeOut(BaseModel):
    id: int
    node_id: str
    mission_id: Optional[int] = None
    deploy_x: Optional[float] = None
    deploy_y: Optional[float] = None
    deploy_z: Optional[float] = None
    floor_level: int
    is_deployed: bool
    is_online: bool
    deployed_at: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    battery_percent: float
    mesh_hop_count: int
    rssi_to_parent: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    voc_index: Optional[float] = None
    co_ppm: Optional[float] = None
    vibration_g: Optional[float] = None
    motion_detected: bool

    class Config:
        from_attributes = True


class NodeDeployCommand(BaseModel):
    node_id: str
    robot_id: str


class NodeReadingOut(BaseModel):
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    voc_index: Optional[float] = None
    co_ppm: Optional[float] = None
    vibration_rms_g: Optional[float] = None
    motion_detected: bool = False
    battery_voltage: Optional[float] = None

    class Config:
        from_attributes = True
