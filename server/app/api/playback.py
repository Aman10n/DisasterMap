"""Playback API — Mission recording replay."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.mission import Mission
from app.models.map_data import MapSnapshot

router = APIRouter()


@router.get("/missions")
async def list_recorded_missions(db: AsyncSession = Depends(get_db)):
    """List all missions with recordings available."""
    result = await db.execute(
        select(Mission).where(Mission.rosbag_path.isnot(None))
    )
    missions = result.scalars().all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None,
            "rosbag_path": m.rosbag_path,
            "area_explored_m2": m.area_explored_m2,
            "victims_confirmed": m.victims_confirmed,
        }
        for m in missions
    ]


@router.get("/{mission_id}/snapshots")
async def get_playback_snapshots(
    mission_id: int, db: AsyncSession = Depends(get_db)
):
    """Get time-ordered map snapshots for progressive playback."""
    result = await db.execute(
        select(MapSnapshot)
        .where(MapSnapshot.mission_id == mission_id)
        .order_by(MapSnapshot.timestamp)
    )
    snapshots = result.scalars().all()
    return [
        {
            "id": s.id,
            "timestamp": s.timestamp.isoformat() if s.timestamp else None,
            "total_voxels": s.total_voxels,
            "occupied_voxels": s.occupied_voxels,
            "mesh_path": s.mesh_path,
        }
        for s in snapshots
    ]


@router.get("/{mission_id}/trajectory")
async def get_robot_trajectory(mission_id: int, db: AsyncSession = Depends(get_db)):
    """Get the recorded robot trajectory for playback animation."""
    from app.models.robot import RobotTelemetry
    result = await db.execute(
        select(RobotTelemetry)
        .order_by(RobotTelemetry.timestamp)
        .limit(10000)
    )
    telemetry = result.scalars().all()
    return [
        {
            "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            "x": t.pos_x, "y": t.pos_y, "z": t.pos_z,
            "yaw": t.yaw,
        }
        for t in telemetry
    ]
