#!/bin/bash
# ============================================
# DisasterMap — Robot ROS 2 Installation Script
# Installs ROS 2 Humble and all dependencies
# on NVIDIA Jetson Xavier NX (Ubuntu 22.04)
# ============================================

set -e

echo "================================================="
echo " DisasterMap Robot Setup — ROS 2 Humble"
echo "================================================="

# --- Check Ubuntu version ---
if [[ $(lsb_release -rs) != "22.04" ]]; then
    echo "WARNING: This script is designed for Ubuntu 22.04"
fi

# --- ROS 2 Humble Installation ---
echo "[1/6] Installing ROS 2 Humble..."
sudo apt update && sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo apt update
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install -y ros-humble-desktop

# --- Source ROS 2 ---
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source /opt/ros/humble/setup.bash

# --- ROS 2 Packages ---
echo "[2/6] Installing ROS 2 packages..."
sudo apt install -y \
    ros-humble-rtabmap-ros \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-robot-localization \
    ros-humble-realsense2-camera \
    ros-humble-rplidar-ros \
    ros-humble-octomap-ros \
    ros-humble-tf2-ros \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers

# --- Python dependencies ---
echo "[3/6] Installing Python packages..."
pip3 install --user \
    paho-mqtt \
    numpy \
    opencv-python-headless \
    msgpack \
    lz4

# --- MQTT Bridge ---
echo "[4/6] Installing MQTT bridge..."
sudo apt install -y ros-humble-mqtt-client

# --- Build workspace ---
echo "[5/6] Building ROS 2 workspace..."
cd "$(dirname "$0")/.."
source /opt/ros/humble/setup.bash
colcon build --symlink-install

# --- udev rules for sensors ---
echo "[6/6] Setting up udev rules..."
sudo tee /etc/udev/rules.d/99-disastermap.rules << 'EOF'
# Velodyne VLP-16
SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6001", MODE="0666"
# Intel RealSense
SUBSYSTEM=="usb", ATTR{idVendor}=="8086", MODE="0666"
# RPLIDAR
SUBSYSTEM=="usb", ATTR{idVendor}=="10c4", ATTR{idProduct}=="ea60", MODE="0666", SYMLINK+="rplidar"
# ESP32 (for gateway)
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", SYMLINK+="esp32_gateway"
EOF
sudo udevadm control --reload-rules

echo "================================================="
echo " Setup complete! Source your workspace:"
echo " source install/setup.bash"
echo " Then launch: ros2 launch robot_bringup robot_bringup.launch.py"
echo "================================================="
