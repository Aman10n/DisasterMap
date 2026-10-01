"""
Map Data ORM Models — Snapshots, annotations, floor levels.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum, Text, JSON, ForeignKey, Boolean, LargeBinary
)
from app.database import Base


class AnnotationType(str, enum.Enum):
    TEXT_NOTE = "text_note"
    NOGO_ZONE = "nogo_zone"
    WAYPOINT = "waypoint"
    STRUCTURAL_CONCERN = "structural_concern"
    ENTRY_POINT = "entry_point"
    EXIT_POINT = "exit_point"


class MapSnapshot(Base):
    """
    Periodic map state captures for playback.
    Stored as compressed OctoMap binary (.bt) in MinIO.
    """
    __tablename__ = "map_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Map stats at snapshot time
    total_voxels = Column(Integer, default=0)
    occupied_voxels = Column(Integer, default=0)
    free_voxels = Column(Integer, default=0)
    resolution = Column(Float, default=0.05)

    # Storage
    octomap_path = Column(String(500), nullable=True)  # MinIO path
    mesh_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)

    # Bounding box
    min_x = Column(Float, default=0.0)
    min_y = Column(Float, default=0.0)
    min_z = Column(Float, default=0.0)
    max_x = Column(Float, default=0.0)
    max_y = Column(Float, default=0.0)
    max_z = Column(Float, default=0.0)

    file_size_bytes = Column(Integer, default=0)


class MapAnnotation(Base):
    __tablename__ = "map_annotations"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)

    annotation_type = Column(Enum(AnnotationType), nullable=False)
    label = Column(String(255), default="")
    description = Column(Text, default="")

    # Position
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)
    pos_z = Column(Float, default=0.0)
    floor_level = Column(Integer, default=0)

    # For polygon annotations (nogo zones)
    polygon_vertices = Column(JSON, nullable=True)  # [[x1,y1], [x2,y2], ...]

    # Metadata
    created_by = Column(String(100), default="operator")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Injected into robot costmap?
    injected_to_costmap = Column(Boolean, default=False)


class FloorLevel(Base):
    __tablename__ = "floor_levels"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)

    floor_index = Column(Integer, nullable=False)  # 0 = ground, 1 = first floor, -1 = basement
    label = Column(String(100), default="")
    height_min = Column(Float, nullable=False)  # z in meters
    height_max = Column(Float, nullable=False)

    # Staircase detected?
    staircase_x = Column(Float, nullable=True)
    staircase_y = Column(Float, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
