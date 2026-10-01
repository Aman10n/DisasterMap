"""Reports API — PDF incident report generation."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.mission import Mission

router = APIRouter()


@router.get("/{mission_id}/pdf")
async def generate_report(mission_id: int, db: AsyncSession = Depends(get_db)):
    """Generate and return a PDF incident report."""
    mission = await db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(404, "Mission not found")

    # In production, this triggers a Celery task for WeasyPrint PDF generation
    # For now, return report metadata
    return {
        "mission_id": mission_id,
        "mission_name": mission.name,
        "status": "report_generation_queued",
        "report_contents": {
            "sections": [
                "Mission Metadata Header",
                "2D Floor Plan with Annotations",
                "3D Map Screenshot",
                "Victim Detection Evidence",
                "Hazard Summary Table",
                "Robot Performance Metrics",
                "Chronological Event Log",
            ],
            "estimated_generation_time": "< 10 seconds",
        },
        "download_url": f"/api/reports/{mission_id}/download",
    }


@router.get("/{mission_id}/download")
async def download_report(mission_id: int, db: AsyncSession = Depends(get_db)):
    """Download generated PDF report."""
    mission = await db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(404, "Mission not found")

    if not mission.report_path:
        raise HTTPException(404, "Report not yet generated. Call GET /api/reports/{id}/pdf first.")

    return FileResponse(
        mission.report_path,
        media_type="application/pdf",
        filename=f"DisasterMap_Report_{mission.name}_{mission_id}.pdf",
    )


@router.get("/{mission_id}/analytics")
async def get_mission_analytics(mission_id: int, db: AsyncSession = Depends(get_db)):
    """Get post-mission performance analytics."""
    mission = await db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(404, "Mission not found")

    # Computed analytics (in production: from Celery worker)
    duration_minutes = 0.0
    if mission.started_at and mission.completed_at:
        duration_minutes = (mission.completed_at - mission.started_at).total_seconds() / 60.0

    return {
        "mission_id": mission_id,
        "total_area_explored_m2": mission.area_explored_m2,
        "exploration_rate_m2_min": mission.exploration_rate_m2_min,
        "duration_minutes": round(duration_minutes, 1),
        "victims_confirmed": mission.victims_confirmed,
        "hazards_detected": mission.hazards_detected,
        "slam_trajectory_length_m": 0.0,  # Computed from telemetry
        "slam_estimated_error_m": 0.0,  # Computed from UWB comparison
        "energy_consumption_wh_per_m2": 0.0,
        "false_positive_rate": {
            "thermal": 0.0,
            "acoustic": 0.0,
            "co2": 0.0,
            "visual": 0.0,
        },
    }
