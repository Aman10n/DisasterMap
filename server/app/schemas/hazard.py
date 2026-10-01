"""Pydantic schemas for Hazard endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HazardZoneOut(BaseModel):
    id: int
    mission_id: int
    robot_id: Optional[str] = None
    hazard_type: str
    severity: str
    pos_x: float
    pos_y: float
    pos_z: float
    radius: float
    peak_value: Optional[float] = None
    current_value: Optional[float] = None
    threshold: Optional[float] = None
    unit: str
    is_active: bool
    is_nogo_zone: bool
    detected_at: datetime
    description: str

    class Config:
        from_attributes = True


class GasReadingOut(BaseModel):
    timestamp: datetime
    pos_x: float
    pos_y: float
    co_ppm: Optional[float] = None
    methane_ppm: Optional[float] = None
    nh3_ppm: Optional[float] = None
    co2_ppm: Optional[float] = None
    voc_index: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None

    class Config:
        from_attributes = True


class GasHeatmapData(BaseModel):
    """Kriging-interpolated gas concentration surface."""
    gas_type: str
    grid_x: list  # 2D grid x-coordinates
    grid_y: list  # 2D grid y-coordinates
    concentrations: list  # 2D concentration values
    unit: str
    threshold: float
