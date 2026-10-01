"""
DisasterMap — FastAPI Application Factory
Main entry point with CORS, lifespan, and router registration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog
import asyncio

from app.config import get_settings
from app.database import init_db
from app.api import (
    missions,
    robots,
    victims,
    hazards,
    sensors,
    maps,
    teleoperation,
    parameters,
    playback,
    reports,
    websocket,
)
from app.mqtt.consumer import MQTTConsumer

logger = structlog.get_logger()
settings = get_settings()

mqtt_consumer = MQTTConsumer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("DisasterMap API starting up", debug=settings.debug)

    # Initialize database tables
    await init_db()
    logger.info("Database initialized")

    # Start MQTT consumer in background
    mqtt_consumer.set_broadcast_callback(websocket.broadcast)
    mqtt_task = asyncio.create_task(mqtt_consumer.start())
    logger.info("MQTT consumer started")

    yield

    # Shutdown
    mqtt_consumer.stop()
    mqtt_task.cancel()
    logger.info("DisasterMap API shutdown complete")


app = FastAPI(
    title="DisasterMap API",
    description="Disaster Response Robot Environment Mapping Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---
app.include_router(missions.router, prefix="/api/missions", tags=["Missions"])
app.include_router(robots.router, prefix="/api/robots", tags=["Robots"])
app.include_router(victims.router, prefix="/api/victims", tags=["Victims"])
app.include_router(hazards.router, prefix="/api/hazards", tags=["Hazards"])
app.include_router(sensors.router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(maps.router, prefix="/api/maps", tags=["Maps"])
app.include_router(teleoperation.router, prefix="/api/teleop", tags=["Teleoperation"])
app.include_router(parameters.router, prefix="/api/parameters", tags=["Parameters"])
app.include_router(playback.router, prefix="/api/playback", tags=["Playback"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


@app.get("/api/health")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "DisasterMap API",
        "version": "1.0.0",
        "mqtt_connected": mqtt_consumer.connected,
    }
