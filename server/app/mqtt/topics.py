"""
MQTT Topic Constants — All MQTT topic paths used in the system.
Namespaced by robot_id for multi-robot support.
"""


class Topics:
    """MQTT topic templates. Replace {robot_id} at runtime."""

    # --- Robot → Server (Telemetry) ---
    ROBOT_POSE = "robot/{robot_id}/pose"
    ROBOT_BATTERY = "robot/{robot_id}/battery"
    ROBOT_HEARTBEAT = "robot/{robot_id}/heartbeat"
    ROBOT_TELEMETRY = "robot/{robot_id}/telemetry"
    ROBOT_STATUS = "robot/{robot_id}/status"

    # --- SLAM ---
    OCTOMAP_DIFF = "robot/{robot_id}/slam/octomap_diff"
    SLAM_LOOP_CLOSURE = "robot/{robot_id}/slam/loop_closure"
    SLAM_QUALITY = "robot/{robot_id}/slam/quality"

    # --- Perception ---
    VICTIM_DETECTION = "robot/{robot_id}/perception/victim"
    THERMAL_DETECTION = "robot/{robot_id}/perception/thermal"
    ACOUSTIC_DETECTION = "robot/{robot_id}/perception/acoustic"
    CO2_DETECTION = "robot/{robot_id}/perception/co2"
    VISUAL_DETECTION = "robot/{robot_id}/perception/visual"

    # --- Hazards ---
    GAS_READING = "robot/{robot_id}/hazard/gas"
    FIRE_DETECTION = "robot/{robot_id}/hazard/fire"
    STRUCTURAL_ALERT = "robot/{robot_id}/hazard/structural"
    VISIBILITY = "robot/{robot_id}/hazard/visibility"

    # --- IoT Nodes ---
    NODE_READING = "node/{node_id}/reading"
    NODE_HEARTBEAT = "node/{node_id}/heartbeat"

    # --- UWB ---
    UWB_RANGE = "uwb/anchor/{anchor_id}/range"
    UWB_POSITION = "uwb/position"

    # --- Server → Robot (Commands) ---
    CMD_VELOCITY = "robot/{robot_id}/cmd/velocity"
    CMD_NAV_GOAL = "robot/{robot_id}/cmd/nav_goal"
    CMD_DROP_NODE = "robot/{robot_id}/cmd/drop_node"
    CMD_RETURN_BASE = "robot/{robot_id}/cmd/return_base"
    CMD_STOP = "robot/{robot_id}/cmd/stop"
    CMD_PARAMETER = "robot/{robot_id}/cmd/parameter"
    CMD_ARM = "robot/{robot_id}/cmd/arm"

    # --- Costmap injection ---
    CMD_NOGO_ZONE = "robot/{robot_id}/cmd/nogo_zone"

    # --- Mission ---
    MISSION_STATE = "mission/state"
    MISSION_ALERT = "mission/alert"

    # --- LoRa fallback ---
    LORA_STATE = "lora/{robot_id}/state"

    @classmethod
    def for_robot(cls, template: str, robot_id: str) -> str:
        """Resolve a topic template for a specific robot."""
        return template.replace("{robot_id}", robot_id)

    @classmethod
    def for_node(cls, template: str, node_id: str) -> str:
        """Resolve a topic template for a specific IoT node."""
        return template.replace("{node_id}", node_id)
