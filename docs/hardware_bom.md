# DisasterMap — Hardware Bill of Materials

## Robot Compute
| Item | Quantity | Purpose |
|------|----------|---------|
| NVIDIA Jetson Xavier NX 16GB | 1 | Primary compute: SLAM, AI, Nav2 |
| Raspberry Pi 4B 8GB | 1 | Secondary: gas sensors, audio, ESP32 gateway |

## Sensors (On-Robot)
| Item | Quantity | Interface | Purpose |
|------|----------|-----------|---------|
| Velodyne VLP-16 3D LiDAR | 1 | Ethernet | Primary SLAM (100m range) |
| RPLIDAR A3 (alternative) | 1 | USB | Lower-cost 2D SLAM (25m) |
| Intel RealSense D435i | 1 | USB 3.0 | RGB-D + IMU for visual SLAM |
| FLIR Lepton 3.5 | 1 | SPI | Thermal imaging (160×120) |
| BNO085 9-DoF IMU | 1 | UART | High-rate IMU (400Hz) |
| MQ-2 Gas Sensor | 1 | Analog (ADC) | Methane, LPG, CO |
| MQ-9 Gas Sensor | 1 | Analog (ADC) | CO, flammable gases |
| MQ-135 Gas Sensor | 1 | Analog (ADC) | NH₃, benzene, smoke |
| MH-Z19B CO₂ Sensor | 1 | UART | NDIR CO₂ (0-5000ppm) |
| ICS-43434 MEMS Microphone | 4 | I2S | Tetrahedral acoustic array |
| DWM1001C UWB Tag | 1 | SPI | Indoor positioning tag |
| Optical Wheel Encoders | 2 | Quadrature | 1024 CPR odometry |
| Wide-Angle Action Camera | 1 | USB-UVC | Teleoperation video feed |

## Deployable IoT Nodes (×5)
| Item | Per Node | Interface | Purpose |
|------|----------|-----------|---------|
| ESP32-S3 WROOM | 1 | — | MCU (dual-core 240MHz) |
| BME688 | 1 | I2C | Temp, humidity, pressure, VOC |
| MQ-7 CO Sensor | 1 | Analog | Carbon monoxide detection |
| MPU6050 | 1 | I2C | Vibration/acceleration |
| PIR Motion Sensor | 1 | Digital | Passive infrared motion |
| 2600mAh LiPo + TP4056 | 1 | — | 12-hour battery life |

## Infrastructure
| Item | Quantity | Purpose |
|------|----------|---------|
| DWM1001-DEV UWB Anchor Kit | 4 | Indoor positioning anchors |
| LoRa SX1276 Module (915MHz) | 2 | Fallback telemetry (robot + base) |
| ESP32 MQTT Gateway | 1 | ESP-NOW → WiFi → MQTT bridge |
| 5GHz WiFi Router (802.11ac) | 1 | Primary radio link |
