"""
Parameter Override ORM Model — Real-time algorithm tuning log.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from app.database import Base


class ParameterOverride(Base):
    __tablename__ = "parameter_overrides"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    robot_id = Column(String(50), nullable=True)

    parameter_name = Column(String(255), nullable=False)
    previous_value = Column(Float, nullable=True)
    new_value = Column(Float, nullable=False)

    changed_by = Column(String(100), default="operator")
    changed_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(Text, default="")
