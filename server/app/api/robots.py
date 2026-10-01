"""Robots API — Fleet management and command routing."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.robot import Robot
from app.schemas.robot import RobotCreate, RobotCommand, RobotOut
from app.mqtt.publisher import publisher

router = APIRouter()


@router.get("/", response_model=List[RobotOut])
async def list_robots(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Robot))
    return result.scalars().all()


@router.post("/", response_model=RobotOut)
async def register_robot(data: RobotCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Robot).where(Robot.robot_id == data.robot_id))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Robot {data.robot_id} already registered")
    robot = Robot(**data.model_dump())
    db.add(robot)
    await db.flush()
    await db.refresh(robot)
    return robot


@router.get("/{robot_id}", response_model=RobotOut)
async def get_robot(robot_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Robot).where(Robot.robot_id == robot_id))
    robot = result.scalar_one_or_none()
    if not robot:
        raise HTTPException(404, f"Robot {robot_id} not found")
    return robot


@router.post("/{robot_id}/command")
async def send_command(robot_id: str, cmd: RobotCommand, db: AsyncSession = Depends(get_db)):
    """Send a command to a robot via MQTT."""
    result = await db.execute(select(Robot).where(Robot.robot_id == robot_id))
    robot = result.scalar_one_or_none()
    if not robot:
        raise HTTPException(404, f"Robot {robot_id} not found")

    if cmd.command_type == "velocity":
        publisher.send_velocity(robot_id, cmd.linear_x, cmd.linear_y, cmd.angular_z)
    elif cmd.command_type == "nav_goal":
        if cmd.goal_x is None or cmd.goal_y is None:
            raise HTTPException(400, "goal_x and goal_y required for nav_goal")
        publisher.send_nav_goal(robot_id, cmd.goal_x, cmd.goal_y)
    elif cmd.command_type == "drop_node":
        node_id = cmd.data.get("node_id", "")
        if not node_id:
            raise HTTPException(400, "node_id required in data")
        publisher.send_drop_node(robot_id, node_id)
    elif cmd.command_type == "return_to_base":
        publisher.send_return_to_base(robot_id)
    elif cmd.command_type == "stop":
        publisher.send_stop(robot_id)
    else:
        raise HTTPException(400, f"Unknown command type: {cmd.command_type}")

    return {"status": "sent", "robot_id": robot_id, "command": cmd.command_type}


@router.post("/{robot_id}/assign-mission/{mission_id}")
async def assign_mission(robot_id: str, mission_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Robot).where(Robot.robot_id == robot_id))
    robot = result.scalar_one_or_none()
    if not robot:
        raise HTTPException(404, f"Robot {robot_id} not found")
    robot.mission_id = mission_id
    return {"status": "assigned", "robot_id": robot_id, "mission_id": mission_id}
