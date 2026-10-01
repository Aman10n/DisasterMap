"""Hazards API — Hazard zones, gas readings, and heatmap data."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.database import get_db
from app.models.hazard import HazardZone, GasReading
from app.schemas.hazard import HazardZoneOut, GasReadingOut, GasHeatmapData
from app.services.gas_interpolation import get_gas_interpolator

router = APIRouter()


@router.get("/zones", response_model=List[HazardZoneOut])
async def list_hazard_zones(mission_id: int = None, active_only: bool = True, db: AsyncSession = Depends(get_db)):
    query = select(HazardZone)
    if mission_id:
        query = query.where(HazardZone.mission_id == mission_id)
    if active_only:
        query = query.where(HazardZone.is_active == True)
    result = await db.execute(query.order_by(desc(HazardZone.detected_at)))
    return result.scalars().all()


@router.get("/gas-readings", response_model=List[GasReadingOut])
async def list_gas_readings(
    mission_id: int, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(GasReading)
        .where(GasReading.mission_id == mission_id)
        .order_by(desc(GasReading.timestamp))
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/heatmap/{mission_id}/{gas_type}")
async def get_gas_heatmap(mission_id: int, gas_type: str):
    """Get kriging-interpolated gas concentration surface."""
    interpolator = get_gas_interpolator(mission_id)
    result = interpolator.interpolate(gas_type)
    if result is None:
        return {"error": "Insufficient data for interpolation", "sample_count": 0}
    return result


@router.get("/zones/{zone_id}", response_model=HazardZoneOut)
async def get_hazard_zone(zone_id: int, db: AsyncSession = Depends(get_db)):
    zone = await db.get(HazardZone, zone_id)
    if not zone:
        raise HTTPException(404, "Hazard zone not found")
    return zone


@router.patch("/zones/{zone_id}/resolve")
async def resolve_hazard(zone_id: int, db: AsyncSession = Depends(get_db)):
    zone = await db.get(HazardZone, zone_id)
    if not zone:
        raise HTTPException(404, "Hazard zone not found")
    from datetime import datetime
    zone.is_active = False
    zone.resolved_at = datetime.utcnow()
    return {"status": "resolved", "zone_id": zone_id}
