"""Missions API — CRUD + state machine transitions + timeline."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.mission import Mission, MissionEvent, MissionState
from app.schemas.mission import MissionCreate, MissionTransition, MissionOut, MissionEventOut, MissionSummary
from app.services.mission_fsm import MissionFSM

router = APIRouter()


@router.get("/", response_model=List[MissionSummary])
async def list_missions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Mission).order_by(desc(Mission.created_at)))
    return result.scalars().all()


@router.post("/", response_model=MissionOut)
async def create_mission(data: MissionCreate, db: AsyncSession = Depends(get_db)):
    mission = Mission(**data.model_dump())
    db.add(mission)
    await db.flush()
    await db.refresh(mission)
    return mission


@router.get("/{mission_id}", response_model=MissionOut)
async def get_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    mission = await db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(404, "Mission not found")
    return mission


@router.patch("/{mission_id}/transition", response_model=MissionOut)
async def transition_mission(
    mission_id: int, data: MissionTransition, db: AsyncSession = Depends(get_db)
):
    mission = await db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(404, "Mission not found")

    # Validate transition
    valid, reason = MissionFSM.validate_transition(
        mission.state, data.target_state, data.operator_override
    )
    if not valid:
        raise HTTPException(400, reason)

    # Log event
    event = MissionEvent(
        mission_id=mission.id,
        event_type="state_change",
        severity="info",
        title=f"State: {mission.state.value} → {data.target_state.value}",
        description=data.reason,
        from_state=mission.state.value,
        to_state=data.target_state.value,
    )
    db.add(event)

    # Update timestamps
    old_state = mission.state
    mission.state = data.target_state
    if data.target_state == MissionState.DEPLOYED:
        mission.started_at = datetime.utcnow()
    elif data.target_state == MissionState.MISSION_COMPLETE:
        mission.completed_at = datetime.utcnow()

    await db.flush()
    await db.refresh(mission)
    return mission


@router.get("/{mission_id}/timeline", response_model=List[MissionEventOut])
async def get_timeline(mission_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MissionEvent)
        .where(MissionEvent.mission_id == mission_id)
        .order_by(desc(MissionEvent.timestamp))
    )
    return result.scalars().all()


@router.get("/{mission_id}/precheck")
async def get_precheck(mission_id: int):
    """Get pre-deployment system check items."""
    items = MissionFSM.get_precheck_items()
    # In production, each item would query actual robot status
    for item in items:
        item["status"] = "pending"
        item["message"] = "Awaiting robot connection"
    return {"checks": items, "all_passed": False}


@router.get("/{mission_id}/available-transitions")
async def get_available_transitions(mission_id: int, db: AsyncSession = Depends(get_db)):
    mission = await db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(404, "Mission not found")
    return {
        "current_state": mission.state.value,
        "available": MissionFSM.get_available_transitions(mission.state),
    }
