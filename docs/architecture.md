# DisasterMap — System Architecture

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    DISASTER SITE                         │
│                                                          │
│  ┌──────────┐   ESP-NOW    ┌──────────┐                 │
│  │ IoT Node │ ──────────── │ IoT Node │                 │
│  └──────────┘   mesh       └──────────┘                 │
│       │                         │                        │
│       └────────────┬────────────┘                        │
│                    │                                     │
│  ┌─────────────────▼──────────────────┐                 │
│  │         ROBOT (Jetson NX)          │                  │
│  │  ┌────────┐ ┌──────┐ ┌─────────┐  │                 │
│  │  │ SLAM   │ │ Nav2 │ │Percept. │  │                  │
│  │  │(RTAB)  │ │(DWB) │ │(YOLO+)  │  │                 │
│  │  └────────┘ └──────┘ └─────────┘  │                  │
│  │  ┌────────┐ ┌──────┐ ┌─────────┐  │                 │
│  │  │Hazard  │ │IoT   │ │ MQTT    │  │                  │
│  │  │Monitor │ │Bridge│ │ Bridge  │  │                  │
│  │  └────────┘ └──────┘ └────┬────┘  │                  │
│  └───────────────────────────┼───────┘                   │
│                              │                           │
│  ┌──────────┐               │   ┌──────────┐            │
│  │UWB Anchor│               │   │UWB Anchor│            │
│  └──────────┘               │   └──────────┘            │
└─────────────────────────────┼───────────────────────────┘
                              │ 5GHz WiFi / LoRa fallback
                              │
┌─────────────────────────────▼───────────────────────────┐
│                  COMMAND CENTER                          │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Docker Compose Stack                │    │
│  │                                                   │    │
│  │  ┌──────────┐  ┌─────────┐  ┌──────────────┐   │    │
│  │  │Mosquitto │  │ Redis   │  │ TimescaleDB  │   │    │
│  │  │  MQTT    │  │ Cache   │  │  + PostGIS   │   │    │
│  │  └─────┬────┘  └────┬────┘  └───────┬──────┘   │    │
│  │        │             │               │           │    │
│  │  ┌─────▼─────────────▼───────────────▼──────┐   │    │
│  │  │           FastAPI Server                  │   │    │
│  │  │  Mission FSM │ Victim Fusion │ Map Proc.  │   │    │
│  │  │  Gas Interp. │ Fleet Coord.  │ UWB Trilat │   │    │
│  │  └──────────────────────┬───────────────────┘   │    │
│  │                         │ WebSocket              │    │
│  │  ┌──────────────────────▼───────────────────┐   │    │
│  │  │        Nginx (Reverse Proxy)              │   │    │
│  │  └──────────────────────┬───────────────────┘   │    │
│  │                         │ :3000                  │    │
│  │  ┌──────────────────────▼───────────────────┐   │    │
│  │  │     React Dashboard (Three.js)            │   │    │
│  │  │  LiveMap│Fleet│Victims│Hazards│TeleOp     │   │    │
│  │  └─────────────────────────────────────────┘   │    │
│  │                                                   │    │
│  │  ┌──────────┐  ┌──────────┐                      │    │
│  │  │ Celery   │  │  MinIO   │                      │    │
│  │  │ Worker   │  │ Storage  │                      │    │
│  │  └──────────┘  └──────────┘                      │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  Operator → Browser → localhost:3000                     │
└──────────────────────────────────────────────────────────┘
```

## Mission State Machine

```
IDLE → PRECHECK → DEPLOYED → EXPLORING ─┬─→ HAZARD_RESPONSE ─→ EXPLORING
                                          ├─→ VICTIM_CONFIRMED ─→ EXPLORING
                                          ├─→ MANUAL_OVERRIDE ──→ EXPLORING
                                          └─→ RETURN_TO_BASE ──→ MISSION_COMPLETE → IDLE
```

## Sensor Fusion Pipeline

```
Thermal (FLIR 8.7Hz)  ──┐
Acoustic (48kHz beam)  ──┤
CO₂ (MH-Z19B 0.5Hz)   ──┼──→ Kalman Filter ──→ Hypothesis ──→ CONFIRMED (≥3 modalities in 90s)
Visual (YOLOv8 15fps)  ──┘        │
                                   └──→ Dashboard Victim Board + Priority Alert
```
