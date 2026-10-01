"""Maps API — Map snapshots, annotations, floor levels, and mesh data."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.map_data import MapSnapshot, MapAnnotation, FloorLevel, AnnotationType
from app.schemas.map import MapAnnotationCreate, MapAnnotationOut, MapSnapshotOut, FloorLevelOut
from app.services.map_processor import get_map_processor
from app.mqtt.publisher import publisher

router = APIRouter()


@router.get("/{mission_id}/mesh")
async def get_current_mesh(mission_id: int):
    """Get the current 3D mesh for the mission's map."""
    processor = get_map_processor(mission_id)
    mesh = processor.generate_mesh()
    return mesh


@router.get("/{mission_id}/stats")
async def get_map_stats(mission_id: int):
    """Get map statistics (voxel counts, resolution)."""
    processor = get_map_processor(mission_id)
    return processor.stats


@router.get("/{mission_id}/floor-slice")
async def get_floor_slice(mission_id: int, z_min: float = -0.3, z_max: float = 0.3):
    """Get 2D floor plan slice at specified height range."""
    processor = get_map_processor(mission_id)
    points = processor.get_floor_slice(z_min, z_max)
    return {"points": points, "z_min": z_min, "z_max": z_max}


@router.get("/{mission_id}/annotations", response_model=List[MapAnnotationOut])
async def list_annotations(mission_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MapAnnotation)
        .where(MapAnnotation.mission_id == mission_id)
        .where(MapAnnotation.is_active == True)
    )
    return result.scalars().all()


@router.post("/{mission_id}/annotations", response_model=MapAnnotationOut)
async def create_annotation(
    mission_id: int, data: MapAnnotationCreate, db: AsyncSession = Depends(get_db)
):
    annotation = MapAnnotation(
        mission_id=mission_id,
        **data.model_dump(),
    )
    db.add(annotation)

    # If it's a nogo zone, inject into robot costmaps via MQTT
    if data.annotation_type == "nogo_zone" and data.polygon_vertices:
        # Send to all robots (broadcast)
        publisher.send_nogo_zone("all", data.polygon_vertices)
        annotation.injected_to_costmap = True

    await db.flush()
    await db.refresh(annotation)
    return annotation


@router.delete("/{mission_id}/annotations/{annotation_id}")
async def delete_annotation(
    mission_id: int, annotation_id: int, db: AsyncSession = Depends(get_db)
):
    annotation = await db.get(MapAnnotation, annotation_id)
    if not annotation or annotation.mission_id != mission_id:
        raise HTTPException(404, "Annotation not found")
    annotation.is_active = False
    return {"status": "deleted", "id": annotation_id}


@router.get("/{mission_id}/floors", response_model=List[FloorLevelOut])
async def list_floors(mission_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(FloorLevel).where(FloorLevel.mission_id == mission_id)
    )
    return result.scalars().all()


@router.get("/{mission_id}/snapshots", response_model=List[MapSnapshotOut])
async def list_snapshots(
    mission_id: int, limit: int = 50, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MapSnapshot)
        .where(MapSnapshot.mission_id == mission_id)
        .order_by(MapSnapshot.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()
