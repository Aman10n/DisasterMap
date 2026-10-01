"""Pydantic schemas for Map endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class MapAnnotationCreate(BaseModel):
    annotation_type: str  # text_note, nogo_zone, waypoint, structural_concern
    label: str = ""
    description: str = ""
    pos_x: float
    pos_y: float
    pos_z: float = 0.0
    floor_level: int = 0
    polygon_vertices: Optional[List[List[float]]] = None


class MapAnnotationOut(BaseModel):
    id: int
    mission_id: int
    annotation_type: str
    label: str
    description: str
    pos_x: float
    pos_y: float
    pos_z: float
    floor_level: int
    polygon_vertices: Optional[list] = None
    created_by: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class MapSnapshotOut(BaseModel):
    id: int
    mission_id: int
    timestamp: datetime
    total_voxels: int
    occupied_voxels: int
    free_voxels: int
    resolution: float
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float
    file_size_bytes: int

    class Config:
        from_attributes = True


class FloorLevelOut(BaseModel):
    id: int
    floor_index: int
    label: str
    height_min: float
    height_max: float
    staircase_x: Optional[float] = None
    staircase_y: Optional[float] = None

    class Config:
        from_attributes = True
