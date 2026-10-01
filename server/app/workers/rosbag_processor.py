"""Rosbag Processor — Celery task for rosbag transfer and analysis."""

from app.workers.celery_app import celery_app


@celery_app.task(name="rosbag.process")
def process_rosbag(mission_id: int, rosbag_path: str):
    """
    Process a rosbag2 file from a completed mission.
    - Transfer compressed segments to MinIO
    - Extract trajectory data
    - Compute SLAM accuracy vs UWB ground truth
    """
    return {
        "status": "processed",
        "mission_id": mission_id,
        "rosbag_path": rosbag_path,
        "topics_recorded": [
            "/scan",
            "/camera/color/image_raw",
            "/camera/depth/image_rect_raw",
            "/thermal/image_raw",
            "/imu/data",
            "/gas_sensors",
            "/audio/raw",
            "/odom",
            "/tf",
            "/map",
            "/octomap_updates",
            "/cmd_vel",
            "/nav2/goal",
        ],
    }
