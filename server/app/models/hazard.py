"""
Hazard ORM Models — Gas, fire, structural with TimescaleDB hypertables.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Enum, JSON, ForeignKey, Boolean, Text
)
from app.database import Base


class HazardType(str, enum.Enum):
    GAS_CO = "gas_co"
    GAS_METHANE = "gas_methane"
    GAS_NH3 = "gas_nh3"
    GAS_CO2 = "gas_co2"
    FIRE_ACTIVE = "fire_active"
    FIRE_HOT_DEBRIS = "fire_hot_debris"
    FIRE_THERMAL_EXPOSURE = "fire_thermal_exposure"
    STRUCTURAL_VIBRATION = "structural_vibration"
    STRUCTURAL_CEILING_SAG = "structural_ceiling_sag"
    STRUCTURAL_WALL_LEAN = "structural_wall_lean"
    STRUCTURAL_FLOOR_VOID = "structural_floor_void"
    SMOKE = "smoke"


class HazardSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"  # IDLH level


class HazardZone(Base):
    __tablename__ = "hazard_zones"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    robot_id = Column(String(50), nullable=True)

    hazard_type = Column(Enum(HazardType), nullable=False)
    severity = Column(Enum(HazardSeverity), default=HazardSeverity.MEDIUM)

    # Position (center of zone)
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)
    pos_z = Column(Float, nullable=False)
    radius = Column(Float, default=3.0)  # meters

    # Values
    peak_value = Column(Float, nullable=True)  # ppm, °C, g-force
    current_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    unit = Column(String(20), default="")

    # Status
    is_active = Column(Boolean, default=True)
    is_nogo_zone = Column(Boolean, default=False)  # Injected into costmap
    detected_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    description = Column(Text, default="")
    data = Column(JSON, default=dict)


class GasReading(Base):
    """Time-series gas sensor readings — TimescaleDB hypertable candidate."""
    __tablename__ = "gas_readings"

    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    robot_id = Column(String(50), nullable=True)
    node_id = Column(String(50), nullable=True)  # IoT node if from deployable sensor
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Position where reading was taken
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)
    pos_z = Column(Float, nullable=False)

    # Gas values (ppm)
    co_ppm = Column(Float, nullable=True)
    methane_ppm = Column(Float, nullable=True)
    nh3_ppm = Column(Float, nullable=True)
    co2_ppm = Column(Float, nullable=True)
    voc_index = Column(Float, nullable=True)
    smoke_density = Column(Float, nullable=True)

    # Ambient
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)


class ThermalReading(Base):
    """Thermal camera reading for fire/heat hazard mapping."""
    __tablename__ = "thermal_readings"

    id = Column(Integer, primary_key=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    robot_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, nullable=False)
    pos_z = Column(Float, nullable=False)

    max_temperature = Column(Float, nullable=False)
    min_temperature = Column(Float, nullable=False)
    avg_temperature = Column(Float, nullable=False)

    classification = Column(String(50), nullable=True)  # active_fire, hot_debris, thermal_exposure, safe
    hot_region_count = Column(Integer, default=0)
    thermal_image_path = Column(String(500), nullable=True)
