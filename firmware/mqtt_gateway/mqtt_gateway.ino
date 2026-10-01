/*
 * DisasterMap — ESP-NOW to MQTT Gateway
 * Receives sensor data from deployed nodes via ESP-NOW,
 * publishes to Mosquitto MQTT broker via WiFi.
 */

#include <WiFi.h>
#include <esp_now.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ===== WiFi Configuration =====
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";

// ===== MQTT Configuration =====
const char* MQTT_SERVER = "YOUR_MQTT_SERVER_IP";
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "dm-gateway";

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

// ===== Sensor Packet (must match sensor_node struct) =====
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

void setup() {
  Serial.begin(115200);
  Serial.println("\n=== DisasterMap MQTT Gateway ===");

  // Connect WiFi
  WiFi.mode(WIFI_AP_STA);  // AP+STA for ESP-NOW + WiFi coexistence
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\nWiFi connected: %s\n", WiFi.localIP().toString().c_str());

  // MQTT
  mqtt.setServer(MQTT_SERVER, MQTT_PORT);
  reconnectMQTT();

  // ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed!");
    return;
  }
  esp_now_register_recv_cb(onDataReceived);
  Serial.println("Gateway ready — listening for ESP-NOW packets");
}

void loop() {
  if (!mqtt.connected()) reconnectMQTT();
  mqtt.loop();
  delay(10);
}

void onDataReceived(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  if (len != sizeof(SensorPacket)) return;

  SensorPacket pkt;
  memcpy(&pkt, data, sizeof(pkt));

  // Build JSON
  StaticJsonDocument<512> doc;
  doc["node_id"] = pkt.node_id;
  doc["temperature"] = pkt.temperature;
  doc["humidity"] = pkt.humidity;
  doc["pressure"] = pkt.pressure;
  doc["voc_index"] = pkt.voc_index;
  doc["co_ppm"] = pkt.co_ppm;
  doc["vibration_rms"] = pkt.vibration_rms;
  doc["motion_detected"] = (bool)pkt.motion_detected;
  doc["battery_voltage"] = pkt.battery_voltage;
  doc["uptime_ms"] = pkt.uptime_ms;

  char payload[512];
  serializeJson(doc, payload);

  // Publish to MQTT
  char topic[64];
  snprintf(topic, sizeof(topic), "node/%s/reading", pkt.node_id);
  mqtt.publish(topic, payload);

  Serial.printf("FWD: %s → %s\n", pkt.node_id, topic);
}

void reconnectMQTT() {
  while (!mqtt.connected()) {
    Serial.println("Connecting to MQTT...");
    if (mqtt.connect(MQTT_CLIENT_ID)) {
      Serial.println("MQTT connected");
    } else {
      Serial.printf("MQTT failed (rc=%d), retrying...\n", mqtt.state());
      delay(2000);
    }
  }
}
