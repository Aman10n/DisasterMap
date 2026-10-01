# Hardware bill of materials

This bill of materials describes the reference hardware envisioned for DisasterMap. It is not a procurement guarantee: confirm availability, regional radio rules, voltage levels, environmental ratings, and mechanical compatibility before purchasing.

## Robot compute

| Item | Quantity | Purpose | Notes |
|---|---:|---|---|
| NVIDIA Jetson Xavier NX 16 GB | 1 | SLAM, perception, and Nav2 | Or a supported modern Jetson equivalent |
| Raspberry Pi 4B 8 GB | 1 | Sensor and gateway workloads | Optional secondary computer |
| Industrial microSD or NVMe storage | 1 | OS, models, logs, and rosbags | Prefer high-endurance media |
| Regulated DC power supplies | As required | Stable compute and sensor rails | Size for transient loads |

## Robot sensing

| Item | Quantity | Interface | Intended role |
|---|---:|---|---|
| Velodyne VLP-16 | 1 | Ethernet | Reference 3D LiDAR for SLAM |
| RPLIDAR A3 | 1 | USB | Lower-cost 2D LiDAR alternative |
| Intel RealSense D435i | 1 | USB 3 | RGB-D and visual-inertial input |
| FLIR Lepton 3.5 | 1 | SPI | Thermal anomaly imaging |
| BNO085 IMU | 1 | UART/I2C | High-rate orientation and acceleration |
| MQ-2 gas sensor | 1 | Analog | Smoke and combustible-gas prototype sensing |
| MQ-9 gas sensor | 1 | Analog | Carbon monoxide and flammable-gas prototype sensing |
| MQ-135 gas sensor | 1 | Analog | Air-quality prototype sensing |
| MH-Z19B | 1 | UART | NDIR carbon-dioxide measurement |
| ICS-43434 microphones | 4 | I2S | Experimental acoustic array |
| DWM1001C UWB tag | 1 | SPI/UART | Indoor ranging reference |
| Wheel encoders | 2 | Quadrature | Chassis odometry |
| Wide-angle UVC camera | 1 | USB | Operator video feed |

> MQ-series sensors require heater control, warm-up, calibration, compensation, and application-specific validation. They must not be treated as certified life-safety instruments.

## Mobility and safety

| Item | Quantity | Purpose |
|---|---:|---|
| Differential-drive chassis and motors | 1 set | Robot mobility |
| Motor drivers with current limiting | 1 set | Controlled motor power |
| Main battery with BMS | 1 | Energy storage and protection |
| Hardware emergency-stop circuit | 1 | Independent actuator power isolation |
| Bump sensors | 2 or more | Contact-level collision detection |
| Status beacon and audible indicator | 1 each | Nearby responder awareness |
| Protective enclosure and cable glands | As required | Dust, impact, and strain protection |

## Deployable sensor node (per node)

| Item | Quantity | Interface | Intended role |
|---|---:|---|---|
| ESP32-S3 WROOM | 1 | — | Node controller and ESP-NOW radio |
| BME688 | 1 | I2C | Temperature, humidity, pressure, and VOC index |
| MQ-7 | 1 | Analog | Prototype carbon-monoxide sensing |
| MPU6050 | 1 | I2C | Vibration and acceleration |
| PIR motion sensor | 1 | Digital | Passive infrared motion indication |
| 2600 mAh LiPo with protection | 1 | Power | Portable supply |
| Charger and regulator | 1 | Power | Safe charging and stable voltage rails |
| Rugged vented enclosure | 1 | — | Mechanical and environmental protection |

The firmware currently models five sensor nodes, but the network size should be determined through measured radio, latency, collision, and battery tests.

## Command-center infrastructure

| Item | Quantity | Purpose |
|---|---:|---|
| Development workstation | 1 | Docker services and operator dashboard |
| 5 GHz Wi-Fi access point | 1 | Primary robot-to-command-center link |
| ESP32 MQTT gateway | 1 | ESP-NOW to MQTT bridge |
| DWM1001-DEV anchors | 4 or more | UWB reference geometry |
| SX1276 LoRa modules | 2 | Experimental low-bandwidth fallback |
| Uninterruptible power supply | 1 | Command-center continuity |

Use only locally permitted radio bands and power levels. LoRa frequency selection varies by country.

## Integration checklist

Before controlled hardware testing:

- verify every voltage rail and common ground;
- measure peak compute, motor, heater, and radio current;
- calibrate gas, IMU, camera, LiDAR, encoder, and UWB devices;
- document coordinate frames and rigid-body transforms;
- validate emergency-stop behavior without network or software assistance;
- add fuses, strain relief, thermal protection, and battery containment;
- test loss of Wi-Fi, MQTT, localization, and sensor input;
- confirm that simulated data is disabled and visibly absent;
- retain manufacturer datasheets and calibration records.
