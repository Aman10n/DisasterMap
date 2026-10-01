"""Victims API — Victim records, hypotheses, and evidence."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.victim import VictimRecord, VictimHypothesis, VictimStatus
from app.schemas.victim import VictimRecordOut, VictimHypothesisOut, VictimStatusUpdate

router = APIRouter()


@router.get("/", response_model=List[VictimRecordOut])
async def list_victims(mission_id: int = None, db: AsyncSession = Depends(get_db)):
    query = select(VictimRecord)
    if mission_id:
        query = query.where(VictimRecord.mission_id == mission_id)
    result = await db.execute(query.order_by(VictimRecord.confirmed_at.desc()))
    return result.scalars().all()


@router.get("/hypotheses", response_model=List[VictimHypothesisOut])
async def list_hypotheses(mission_id: int = None, db: AsyncSession = Depends(get_db)):
    query = select(VictimHypothesis).where(VictimHypothesis.status == VictimStatus.HYPOTHESIS)
    if mission_id:
        query = query.where(VictimHypothesis.mission_id == mission_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{victim_id}", response_model=VictimRecordOut)
async def get_victim(victim_id: int, db: AsyncSession = Depends(get_db)):
    victim = await db.get(VictimRecord, victim_id)
    if not victim:
        raise HTTPException(404, "Victim record not found")
    return victim


@router.patch("/{victim_id}/status")
async def update_victim_status(
    victim_id: int, data: VictimStatusUpdate, db: AsyncSession = Depends(get_db)
):
    victim = await db.get(VictimRecord, victim_id)
    if not victim:
        raise HTTPException(404, "Victim record not found")

    if data.status == "rescued":
        victim.status = VictimStatus.RESCUED
        from datetime import datetime
        victim.rescued_at = datetime.utcnow()
    elif data.status == "false_positive":
        victim.status = VictimStatus.FALSE_POSITIVE
    else:
        raise HTTPException(400, f"Invalid status: {data.status}")

    victim.rescue_notes = data.rescue_notes
    return {"status": "updated", "victim_id": victim_id, "new_status": data.status}


@router.get("/{victim_id}/evidence")
async def get_victim_evidence(victim_id: int, db: AsyncSession = Depends(get_db)):
    """Get all evidence associated with a victim record."""
    victim = await db.get(VictimRecord, victim_id)
    if not victim:
        raise HTTPException(404, "Victim record not found")

    return {
        "victim_id": victim_id,
        "thermal_image": victim.thermal_image_path,
        "visual_image": victim.visual_image_path,
        "audio_clip": victim.audio_clip_path,
        "co2_trace": victim.co2_trace_data,
        "pose_keypoints": victim.pose_keypoints,
        "body_visible": victim.body_visible_parts,
        "burial_depth": victim.estimated_burial_depth,
    }
