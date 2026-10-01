"""Sensors API — IoT node deployment, status, and readings."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.sensor_node import IoTNode, NodeReading
from app.schemas.sensor import IoTNodeOut, NodeDeployCommand, NodeReadingOut
from app.mqtt.publisher import publisher

router = APIRouter()


@router.get("/nodes", response_model=List[IoTNodeOut])
async def list_nodes(mission_id: int = None, db: AsyncSession = Depends(get_db)):
    query = select(IoTNode)
    if mission_id:
        query = query.where(IoTNode.mission_id == mission_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/nodes/{node_id}", response_model=IoTNodeOut)
async def get_node(node_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IoTNode).where(IoTNode.node_id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(404, f"Node {node_id} not found")
    return node


@router.post("/deploy")
async def deploy_node(cmd: NodeDeployCommand, db: AsyncSession = Depends(get_db)):
    """Command robot to deploy an IoT sensor node at current location."""
    publisher.send_drop_node(cmd.robot_id, cmd.node_id)
    return {"status": "deploy_command_sent", "node_id": cmd.node_id, "robot_id": cmd.robot_id}


@router.get("/nodes/{node_id}/readings", response_model=List[NodeReadingOut])
async def get_node_readings(
    node_id: str, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(NodeReading)
        .where(NodeReading.node_id == node_id)
        .order_by(NodeReading.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()
