/*
 * IoT Dashboard - ESP32 Integration Example
 * 
 * This code demonstrates how to connect your ESP32 device to the IoT Dashboard
 * and send real-time sensor data via WebSocket connection.
 * 
 * Required Libraries:
 * - ArduinoWebsockets by Markus Sattler
 * - ArduinoJson by Benoit Blanchon
 * - DHT sensor library by Adafruit (if using DHT22)
 * - Adafruit BMP280 Library (if using BMP280)
 * 
 * Hardware Setup:
 * - DHT22: Data pin to GPIO 4
 * - BMP280: I2C (SDA to GPIO 21, SCL to GPIO 22)
 * - LDR (Light sensor): Analog pin A0 (GPIO 36)
 * - PIR Motion sensor: Digital pin GPIO 2
 * - Built-in LED: GPIO 2 (on most ESP32 boards)
 */

#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Adafruit_BMP280.h>
#include <Wire.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server Configuration
const char* websocket_server = "ws://192.168.1.100:5000/socket.io/?EIO=4&transport=websocket";
const char* device_id = "ESP32_001";
const char* device_name = "Living Room Sensor";

// Pin Definitions
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define PIR_PIN 2
#define LDR_PIN 36
#define LED_PIN 2
#define MOTION_LED_PIN 5

// Sensor Objects
DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_BMP280 bmp;

// WebSocket Client
using namespace websockets;
WebsocketsClient client;

// Timing Variables
unsigned long lastSensorRead = 0;
unsigned long lastDataSend = 0;
const unsigned long SENSOR_INTERVAL = 2000; // Read sensors every 2 seconds
const unsigned long DATA_SEND_INTERVAL = 5000; // Send data every 5 seconds

// Sensor Data Structure
struct SensorData {
  float temperature = 0.0;
  float humidity = 0.0;
  float pressure = 0.0;
  int light = 0;
  bool motion = false;
  float voltage = 0.0;
  unsigned long timestamp = 0;
};

SensorData currentData;
bool ledState = false;
int ledBrightness = 50;
int motorSpeed = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("🔌 IoT Dashboard - ESP32 Client Starting...");
  
  // Initialize pins
  pinMode(PIR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(MOTION_LED_PIN, OUTPUT);
  pinMode(LDR_PIN, INPUT);
  
  // Initialize sensors
  dht.begin();
  
  if (!bmp.begin(0x76)) {
    Serial.println("❌ Could not find BMP280 sensor, using simulated data");
  } else {
    Serial.println("✅ BMP280 sensor initialized");
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                    Adafruit_BMP280::SAMPLING_X2,
                    Adafruit_BMP280::SAMPLING_X16,
                    Adafruit_BMP280::FILTER_X16,
                    Adafruit_BMP280::STANDBY_MS_500);
  }
  
  // Connect to WiFi
  connectToWiFi();
  
  // Setup WebSocket connection
  setupWebSocket();
  
  // Register device
  registerDevice();
  
  Serial.println("🚀 Setup complete! Starting main loop...");
}

void loop() {
  // Keep WebSocket connection alive
  client.poll();
  
  // Read sensors at defined interval
  if (millis() - lastSensorRead >= SENSOR_INTERVAL) {
    readSensors();
    lastSensorRead = millis();
  }
  
  // Send data at defined interval
  if (millis() - lastDataSend >= DATA_SEND_INTERVAL) {
    sendSensorData();
    lastDataSend = millis();
  }
  
  // Handle motion detection LED
  if (currentData.motion) {
    digitalWrite(MOTION_LED_PIN, HIGH);
  } else {
    digitalWrite(MOTION_LED_PIN, LOW);
  }
  
  delay(100);
}

void connectToWiFi() {
  Serial.print("📶 Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connected!");
    Serial.print("📍 IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("📡 Signal strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
    ESP.restart();
  }
}

void setupWebSocket() {
  Serial.println("🔗 Setting up WebSocket connection...");
  
  // WebSocket event handlers
  client.onMessage([](WebsocketsMessage message) {
    handleWebSocketMessage(message.data());
  });
  
  client.onEvent([](WebsocketsEvent event, String data) {
    switch (event) {
      case WebsocketsEvent::ConnectionOpened:
        Serial.println("✅ WebSocket Connected!");
        break;
      case WebsocketsEvent::ConnectionClosed:
        Serial.println("❌ WebSocket Disconnected!");
        break;
      case WebsocketsEvent::GotPing:
        Serial.println("💓 WebSocket Ping");
        client.pong();
        break;
      case WebsocketsEvent::GotPong:
        Serial.println("💓 WebSocket Pong");
        break;
    }
  });
  
  // Connect to WebSocket server
  bool connected = client.connect(websocket_server);
  if (connected) {
    Serial.println("🎯 WebSocket connection established!");
  } else {
    Serial.println("❌ WebSocket connection failed!");
    delay(5000);
    ESP.restart();
  }
}

void registerDevice() {
  Serial.println("📝 Registering device with dashboard...");
  
  DynamicJsonDocument doc(512);
  doc["device_id"] = device_id;
  doc["name"] = device_name;
  doc["type"] = "esp32";
  doc["firmware_version"] = "1.0.0";
  doc["capabilities"] = JsonArray();
  doc["capabilities"].add("temperature");
  doc["capabilities"].add("humidity");
  doc["capabilities"].add("pressure");
  doc["capabilities"].add("light");
  doc["capabilities"].add("motion");
  doc["capabilities"].add("led_control");
  
  String message;
  serializeJson(doc, message);
  
  String socketMessage = "42[\"device_register\"," + message + "]";
  client.send(socketMessage);
  
  Serial.println("✅ Device registered!");
}

void readSensors() {
  // Read DHT22 (Temperature & Humidity)
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  
  if (!isnan(temp)) {
    currentData.temperature = temp;
  } else {
    // Simulate temperature if sensor not available
    currentData.temperature = 20.0 + random(-5, 15);
  }
  
  if (!isnan(hum)) {
    currentData.humidity = hum;
  } else {
    // Simulate humidity if sensor not available
    currentData.humidity = 45.0 + random(-10, 20);
  }
  
  // Read BMP280 (Pressure)
  if (bmp.begin(0x76)) {
    currentData.pressure = bmp.readPressure() / 100.0; // Convert Pa to hPa
  } else {
    // Simulate pressure
    currentData.pressure = 1013.0 + random(-20, 20);
  }
  
  // Read LDR (Light sensor)
  int ldrValue = analogRead(LDR_PIN);
  currentData.light = map(ldrValue, 0, 4095, 0, 1000); // Map to lux (approximate)
  
  // Read PIR (Motion sensor)
  currentData.motion = digitalRead(PIR_PIN);
  
  // Read battery voltage (if using battery)
  currentData.voltage = (analogRead(A13) / 4095.0) * 3.3 * 2; // Voltage divider
  
  currentData.timestamp = millis();
  
  // Debug output
  if (millis() % 10000 < 100) { // Print every 10 seconds
    Serial.println("📊 Current sensor readings:");
    Serial.printf("  🌡️  Temperature: %.2f°C\\n", currentData.temperature);
    Serial.printf("  💧 Humidity: %.2f%%\\n", currentData.humidity);
    Serial.printf("  📊 Pressure: %.2f hPa\\n", currentData.pressure);
    Serial.printf("  💡 Light: %d lux\\n", currentData.light);
    Serial.printf("  🚶 Motion: %s\\n", currentData.motion ? "Detected" : "None");
    Serial.printf("  🔋 Voltage: %.2fV\\n", currentData.voltage);
  }
}

void sendSensorData() {
  if (!client.available()) {
    Serial.println("❌ WebSocket not connected, attempting reconnection...");
    setupWebSocket();
    registerDevice();
    return;
  }
  
  DynamicJsonDocument doc(512);
  doc["device_id"] = device_id;
  doc["temperature"] = currentData.temperature;
  doc["humidity"] = currentData.humidity;
  doc["pressure"] = currentData.pressure;
  doc["light"] = currentData.light;
  doc["motion"] = currentData.motion;
  doc["voltage"] = currentData.voltage;
  doc["timestamp"] = WiFi.getTime();
  doc["signal_strength"] = WiFi.RSSI();
  
  String message;
  serializeJson(doc, message);
  
  String socketMessage = "42[\"sensor_data\"," + message + "]";
  bool sent = client.send(socketMessage);
  
  if (sent) {
    Serial.println("📤 Sensor data sent successfully");
  } else {
    Serial.println("❌ Failed to send sensor data");
  }
}

void handleWebSocketMessage(String message) {
  Serial.println("📥 Received command: " + message);
  
  // Parse Socket.IO message format
  if (message.startsWith("42")) {
    // Remove Socket.IO prefix
    String jsonPart = message.substring(2);
    
    DynamicJsonDocument doc(512);
    deserializeJson(doc, jsonPart);
    
    if (doc.size() >= 2) {
      String eventName = doc[0];
      JsonObject commandData = doc[1];
      
      if (eventName == "command") {
        handleDeviceCommand(commandData);
      }
    }
  }
}

void handleDeviceCommand(JsonObject command) {
  String cmd = command["command"];
  String value = command["value"];
  
  Serial.println("🎮 Executing command: " + cmd + " = " + value);
  
  if (cmd == "led_brightness") {
    ledBrightness = value.toInt();
    analogWrite(LED_PIN, map(ledBrightness, 0, 100, 0, 255));
    Serial.printf("💡 LED brightness set to %d%%\\n", ledBrightness);
    
  } else if (cmd == "power") {
    if (value == "on" || value == "true") {
      ledState = true;
      digitalWrite(LED_PIN, HIGH);
      Serial.println("⚡ Device power ON");
    } else {
      ledState = false;
      digitalWrite(LED_PIN, LOW);
      Serial.println("⚡ Device power OFF");
    }
    
  } else if (cmd == "motor_speed") {
    motorSpeed = value.toInt();
    // Here you would control a motor with PWM
    Serial.printf("🔧 Motor speed set to %d%%\\n", motorSpeed);
    
  } else if (cmd == "reset") {
    Serial.println("🔄 Resetting device...");
    delay(1000);
    ESP.restart();
    
  } else if (cmd == "status") {
    sendStatusReport();
    
  } else if (cmd == "calibrate") {
    Serial.println("🔧 Calibrating sensors...");
    // Perform calibration routine
    
  } else if (cmd == "test_led") {
    Serial.println("💡 Testing LED...");
    for (int i = 0; i < 3; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(200);
      digitalWrite(LED_PIN, LOW);
      delay(200);
    }
    
  } else if (cmd == "wifi") {
    // WiFi control would be implemented here
    Serial.println("📶 WiFi command: " + value);
    
  } else if (cmd == "bluetooth") {
    // Bluetooth control would be implemented here
    Serial.println("📱 Bluetooth command: " + value);
    
  } else {
    Serial.println("❓ Unknown command: " + cmd);
  }
}

void sendStatusReport() {
  DynamicJsonDocument doc(512);
  doc["device_id"] = device_id;
  doc["status"] = "online";
  doc["uptime"] = millis();
  doc["free_heap"] = ESP.getFreeHeap();
  doc["wifi_rssi"] = WiFi.RSSI();
  doc["led_state"] = ledState;
  doc["led_brightness"] = ledBrightness;
  doc["motor_speed"] = motorSpeed;
  
  String message;
  serializeJson(doc, message);
  
  String socketMessage = "42[\"device_status\"," + message + "]";
  client.send(socketMessage);
  
  Serial.println("📋 Status report sent");
}

// WiFi connection monitoring
void checkWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi connection lost, reconnecting...");
    connectToWiFi();
    setupWebSocket();
    registerDevice();
  }
}
