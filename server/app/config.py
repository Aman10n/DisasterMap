"""
DisasterMap — Configuration via Pydantic Settings
All config is driven by environment variables (from .env or Docker).
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "DisasterMap"
    debug: bool = True
    secret_key: str = "development-only-replace-before-deployment"

    # --- Database ---
    database_url: str = "postgresql+asyncpg://disastermap:replace-with-a-strong-password@timescaledb:5432/disastermap"

    # --- Redis ---
    redis_url: str = "redis://redis:6379/0"

    # --- MQTT ---
    mqtt_broker_host: str = "mosquitto"
    mqtt_broker_port: int = 1883

    # --- MinIO ---
    minio_endpoint: str = "minio:9000"
    minio_root_user: str = "disastermap-admin"
    minio_root_password: str = "replace-with-a-strong-password"
    minio_bucket: str = "disastermap"

    # --- Celery ---
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    # --- SLAM Defaults ---
    octomap_resolution: float = 0.05  # 5cm voxels
    map_update_interval: float = 2.0  # seconds
    loop_closure_threshold: float = 0.11

    # --- Detection Defaults ---
    thermal_threshold_above_ambient: float = 32.0  # °C
    co2_threshold_above_ambient: float = 600.0  # ppm
    acoustic_confidence_threshold: float = 0.75
    visual_confidence_threshold: float = 0.60

    # --- Gas IDLH Thresholds ---
    co_idlh_ppm: float = 50.0
    methane_lel_percent: float = 10.0
    nh3_idlh_ppm: float = 25.0

    # --- Navigation ---
    max_linear_speed: float = 0.5  # m/s
    max_angular_speed: float = 1.0  # rad/s
    costmap_inflation_radius: float = 0.3  # meters
    thermal_standoff_distance: float = 2.0  # meters

    # --- Battery ---
    battery_low_threshold: float = 15.0  # percent
    battery_critical_threshold: float = 5.0

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
