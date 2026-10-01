"""
Mission Finite State Machine — 9-state lifecycle with transition rules.
Enforces valid transitions, logs all changes, requires operator confirmation
for risk-increasing transitions.
"""

import structlog
from datetime import datetime
from typing import Optional, Tuple
from app.models.mission import MissionState

logger = structlog.get_logger()

# --- Valid State Transitions ---
# Key: current state → Set of allowed target states
VALID_TRANSITIONS = {
    MissionState.IDLE: {MissionState.PRECHECK},
    MissionState.PRECHECK: {MissionState.DEPLOYED, MissionState.IDLE},
    MissionState.DEPLOYED: {MissionState.EXPLORING, MissionState.IDLE},
    MissionState.EXPLORING: {
        MissionState.HAZARD_RESPONSE,
        MissionState.VICTIM_CONFIRMED,
        MissionState.MANUAL_OVERRIDE,
        MissionState.RETURN_TO_BASE,
    },
    MissionState.HAZARD_RESPONSE: {
        MissionState.EXPLORING,
        MissionState.MANUAL_OVERRIDE,
        MissionState.RETURN_TO_BASE,
    },
    MissionState.VICTIM_CONFIRMED: {
        MissionState.EXPLORING,
        MissionState.MANUAL_OVERRIDE,
        MissionState.RETURN_TO_BASE,
    },
    MissionState.MANUAL_OVERRIDE: {
        MissionState.EXPLORING,
        MissionState.RETURN_TO_BASE,
        MissionState.HAZARD_RESPONSE,
    },
    MissionState.RETURN_TO_BASE: {
        MissionState.MISSION_COMPLETE,
        MissionState.MANUAL_OVERRIDE,
    },
    MissionState.MISSION_COMPLETE: {MissionState.IDLE},
}

# States that increase risk — require operator confirmation
RISK_INCREASING = {
    (MissionState.MANUAL_OVERRIDE, MissionState.EXPLORING),
    (MissionState.RETURN_TO_BASE, MissionState.MANUAL_OVERRIDE),
}

# Autonomous transitions — pre-authorized, no operator confirmation needed
AUTONOMOUS_TRANSITIONS = {
    (MissionState.EXPLORING, MissionState.RETURN_TO_BASE),  # Battery low
    (MissionState.EXPLORING, MissionState.HAZARD_RESPONSE),  # Hazard detected
    (MissionState.EXPLORING, MissionState.VICTIM_CONFIRMED),  # Victim confirmed
}


class MissionFSM:
    """Mission state machine with full transition validation."""

    @staticmethod
    def validate_transition(
        current_state: MissionState,
        target_state: MissionState,
        operator_override: bool = False,
    ) -> Tuple[bool, str]:
        """
        Validate a state transition.
        Returns (is_valid, reason).
        """
        if target_state not in VALID_TRANSITIONS.get(current_state, set()):
            return False, (
                f"Invalid transition: {current_state.value} → {target_state.value}. "
                f"Allowed: {[s.value for s in VALID_TRANSITIONS.get(current_state, set())]}"
            )

        transition = (current_state, target_state)

        if transition in RISK_INCREASING and not operator_override:
            return False, (
                f"Transition {current_state.value} → {target_state.value} increases risk. "
                "Operator override required (set operator_override=true)."
            )

        return True, "Transition approved"

    @staticmethod
    def is_autonomous_transition(
        current_state: MissionState, target_state: MissionState
    ) -> bool:
        """Check if this transition is pre-authorized for autonomous execution."""
        return (current_state, target_state) in AUTONOMOUS_TRANSITIONS

    @staticmethod
    def get_available_transitions(current_state: MissionState) -> list:
        """Get list of states available from current state."""
        return [s.value for s in VALID_TRANSITIONS.get(current_state, set())]

    @staticmethod
    def get_precheck_items() -> list:
        """Return list of pre-deployment system check items."""
        return [
            {"id": "ros2_topics", "name": "ROS 2 Topics Publishing", "description": "All ROS 2 topics at expected rates"},
            {"id": "slam_init", "name": "SLAM Initialization", "description": "SLAM engine initialized and producing map"},
            {"id": "sensor_calibration", "name": "Sensor Calibration", "description": "All sensor calibrations within tolerance"},
            {"id": "battery", "name": "Battery Level", "description": "Battery above 30%"},
            {"id": "mqtt_broker", "name": "MQTT Broker", "description": "MQTT broker reachable and accepting connections"},
            {"id": "uwb_anchors", "name": "UWB Anchors", "description": "All 4 UWB anchors responding to ranging requests"},
            {"id": "odometry", "name": "Robot Odometry", "description": "Wheel odometry reporting plausible values"},
            {"id": "camera_feeds", "name": "Camera Feeds", "description": "RGB, depth, and thermal cameras streaming"},
            {"id": "gas_sensors", "name": "Gas Sensors", "description": "Gas sensor array reporting baseline readings"},
            {"id": "nav2_stack", "name": "Nav2 Stack", "description": "Navigation stack active and accepting goals"},
        ]
