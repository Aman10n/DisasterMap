"""Teleoperation API — Manual control, camera feeds, arm control."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.mqtt.publisher import publisher

router = APIRouter()


@router.post("/{robot_id}/velocity")
async def send_velocity(robot_id: str, linear_x: float = 0.0, linear_y: float = 0.0, angular_z: float = 0.0):
    """Send velocity command from joystick (20Hz in production)."""
    publisher.send_velocity(robot_id, linear_x, linear_y, angular_z)
    return {"status": "sent", "linear_x": linear_x, "linear_y": linear_y, "angular_z": angular_z}


@router.post("/{robot_id}/nav-goal")
async def send_nav_goal(robot_id: str, x: float, y: float):
    """Click-to-go: send navigation goal to a map point."""
    publisher.send_nav_goal(robot_id, x, y)
    return {"status": "sent", "goal_x": x, "goal_y": y}


@router.post("/{robot_id}/stop")
async def emergency_stop(robot_id: str):
    """Emergency stop — halt all robot motion."""
    publisher.send_stop(robot_id)
    return {"status": "stopped", "robot_id": robot_id}


@router.post("/{robot_id}/arm")
async def send_arm_command(
    robot_id: str,
    joint_angles: list = None,
    end_effector_xyz: list = None,
):
    """Control 6-DOF robot arm (joint space or Cartesian)."""
    publisher.send_arm_command(robot_id, joints=joint_angles, xyz=end_effector_xyz)
    return {"status": "sent", "mode": "joint" if joint_angles else "cartesian"}


@router.get("/{robot_id}/camera-urls")
async def get_camera_urls(robot_id: str):
    """Get camera stream URLs for the teleoperation view."""
    base = f"http://localhost:8000/api/teleop/{robot_id}"
    return {
        "rgb": f"{base}/stream/rgb",
        "thermal": f"{base}/stream/thermal",
        "depth": f"{base}/stream/depth",
        "wide_angle": f"{base}/stream/wide",
    }
