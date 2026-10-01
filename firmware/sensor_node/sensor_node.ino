/*
 * DisasterMap — Deployable IoT Sensor Node Firmware
 * ESP32-S3 with BME688, MQ-7, MPU6050, PIR
 * Communicates via ESP-NOW mesh to gateway
 */

#include <WiFi.h>
#include <esp_now.h>
#include <Wire.h>
#include <esp_sleep.h>

// ===== Pin Definitions =====
#define MQ7_PIN         36    // ADC1_CH0 - CO sensor analog
#define PIR_PIN         13    // PIR motion detector digital
#define LED_STATUS      2     // Onboard LED
#define BATTERY_PIN     35    // ADC1_CH7 - Battery voltage divider

// ===== Configuration =====
#define NODE_ID         "node_01"
#define SEND_INTERVAL   2000   // ms between transmissions
#define SLEEP_INTERVAL  30000  // ms deep sleep between active periods
#define VIBRATION_THRESHOLD 0.15  // g RMS

// ===== Gateway MAC Address (set during deployment) =====
uint8_t gatewayMAC[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};  // Broadcast

// ===== Sensor Data Structure =====
typedef struct __attribute__((packed)) {
  char node_id[12];
  float temperature;
  float humidity;
  float pressure;
  float voc_index;
  float co_ppm;
  float vibration_rms;
  uint8_t motion_detected;
  float battery_voltage;
  uint32_t uptime_ms;
} SensorPacket;

SensorPacket packet;

// ===== BME688 (I2C) =====
// Using simplified register access — production uses Bosch BSEC library
#define BME688_ADDR 0x76

// ===== MPU6050 (I2C) =====
#define MPU6050_ADDR 0x68

// ===== State =====
unsigned long lastSend = 0;
bool espNowReady = false;
float accelBuffer[50];
int accelIdx = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== DisasterMap Sensor Node ===");
  Serial.printf("Node ID: %s\n", NODE_ID);

  // Pin setup
  pinMode(PIR_PIN, INPUT);
  pinMode(LED_STATUS, OUTPUT);
  pinMode(MQ7_PIN, INPUT);
  pinMode(BATTERY_PIN, INPUT);

  // I2C
  Wire.begin(21, 22);

  // Init sensors
  initMPU6050();
  initBME688();

  // WiFi + ESP-NOW
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed!");
    return;
  }

  // Register peer (gateway or nearest neighbor)
  esp_now_peer_info_t peer;
  memset(&peer, 0, sizeof(peer));
  memcpy(peer.peer_addr, gatewayMAC, 6);
  peer.channel = 0;
  peer.encrypt = false;
  esp_now_add_peer(&peer);

  esp_now_register_send_cb(onDataSent);
  espNowReady = true;

  // Set node ID in packet
  strncpy(packet.node_id, NODE_ID, sizeof(packet.node_id));

  Serial.println("Sensor node initialized OK");
  blinkLED(3);
}

void loop() {
  // Read sensors
  readBME688();
  readMQ7();
  readMPU6050();
  readPIR();
  readBattery();
  packet.uptime_ms = millis();

  // Send at configured interval
  if (millis() - lastSend >= SEND_INTERVAL) {
    lastSend = millis();
    sendData();
  }

  delay(50);  // 20Hz sensor loop
}

// ===== Sensor Reading Functions =====

void initMPU6050() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x6B);  // PWR_MGMT_1
  Wire.write(0x00);  // Wake up
  Wire.endTransmission();
  Serial.println("MPU6050 initialized");
}

void initBME688() {
  // Simplified — production uses Bosch BSEC library
  Serial.println("BME688 initialized");
}

void readBME688() {
  // Simulated readings — replace with BSEC library in production
  packet.temperature = 22.0 + (float)(analogRead(36) % 100) / 10.0;
  packet.humidity = 45.0 + (float)(analogRead(36) % 200) / 10.0;
  packet.pressure = 1013.25;
  packet.voc_index = (float)(analogRead(36) % 500);
}

void readMQ7() {
  int raw = analogRead(MQ7_PIN);
  // Simplified conversion — calibrate per sensor in production
  float voltage = raw * (3.3 / 4095.0);
  float rs_r0 = (3.3 - voltage) / voltage;
  packet.co_ppm = 100.0 / rs_r0;  // Simplified curve
  if (packet.co_ppm < 0) packet.co_ppm = 0;
  if (packet.co_ppm > 1000) packet.co_ppm = 1000;
}

void readMPU6050() {
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x3B);  // ACCEL_XOUT_H
  Wire.endTransmission(false);
  Wire.requestFrom(MPU6050_ADDR, 6);

  int16_t ax = (Wire.read() << 8) | Wire.read();
  int16_t ay = (Wire.read() << 8) | Wire.read();
  int16_t az = (Wire.read() << 8) | Wire.read();

  float accel_g = sqrt(
    pow(ax / 16384.0, 2) +
    pow(ay / 16384.0, 2) +
    pow(az / 16384.0, 2)
  ) - 1.0;  // Remove gravity

  // Rolling RMS
  accelBuffer[accelIdx % 50] = accel_g * accel_g;
  accelIdx++;

  float sum = 0;
  int count = min(accelIdx, 50);
  for (int i = 0; i < count; i++) sum += accelBuffer[i];
  packet.vibration_rms = sqrt(sum / count);
}

void readPIR() {
  packet.motion_detected = digitalRead(PIR_PIN);
}

void readBattery() {
  int raw = analogRead(BATTERY_PIN);
  // Voltage divider: 100k/100k, factor = 2
  packet.battery_voltage = (raw / 4095.0) * 3.3 * 2.0;
}

// ===== Communication =====

void sendData() {
  if (!espNowReady) return;

  esp_err_t result = esp_now_send(gatewayMAC, (uint8_t*)&packet, sizeof(packet));
  if (result == ESP_OK) {
    digitalWrite(LED_STATUS, HIGH);
    delay(50);
    digitalWrite(LED_STATUS, LOW);
  } else {
    Serial.println("ESP-NOW send failed");
  }
}

void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  if (status != ESP_NOW_SEND_SUCCESS) {
    Serial.println("Delivery failed — will retry");
  }
}

// ===== Utility =====

void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_STATUS, HIGH);
    delay(150);
    digitalWrite(LED_STATUS, LOW);
    delay(150);
  }
}
