"""Parameters API — Real-time algorithm parameter tuning."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Dict

from app.database import get_db
from app.models.parameter import ParameterOverride
from app.mqtt.publisher import publisher
from app.config import get_settings

router = APIRouter()

settings = get_settings()

# Tunable parameters with current values (in-memory cache)
_current_params: Dict[str, float] = {
    "frontier_w_distance": 1.0,
    "frontier_w_size": 0.5,
    "frontier_w_hazard": 0.3,
    "thermal_threshold": settings.thermal_threshold_above_ambient,
    "co2_threshold": settings.co2_threshold_above_ambient,
    "acoustic_threshold": settings.acoustic_confidence_threshold,
    "visual_threshold": settings.visual_confidence_threshold,
    "co_idlh_ppm": settings.co_idlh_ppm,
    "methane_lel_percent": settings.methane_lel_percent,
    "nh3_idlh_ppm": settings.nh3_idlh_ppm,
    "max_linear_speed": settings.max_linear_speed,
    "max_angular_speed": settings.max_angular_speed,
    "costmap_inflation_radius": settings.costmap_inflation_radius,
    "thermal_standoff_distance": settings.thermal_standoff_distance,
    "slam_loop_closure_threshold": settings.loop_closure_threshold,
}


@router.get("/")
async def list_parameters():
    """Get all tunable parameters with current values."""
    return _current_params


@router.patch("/{robot_id}")
async def update_parameter(
    robot_id: str,
    param_name: str,
    value: float,
    reason: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Update a parameter in real-time — takes effect within 100ms."""
    if param_name not in _current_params:
        raise HTTPException(400, f"Unknown parameter: {param_name}")

    old_value = _current_params[param_name]
    _current_params[param_name] = value

    # Log the override
    override = ParameterOverride(
        mission_id=1,  # TODO: get from context
        robot_id=robot_id,
        parameter_name=param_name,
        previous_value=old_value,
        new_value=value,
        reason=reason,
    )
    db.add(override)

    # Send to robot via MQTT
    publisher.send_parameter(robot_id, param_name, value)

    return {
        "status": "updated",
        "parameter": param_name,
        "old_value": old_value,
        "new_value": value,
    }
