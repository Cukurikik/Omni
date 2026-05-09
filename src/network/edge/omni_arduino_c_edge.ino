// OMNI IoT & Edge Layer
// Arduino C implementation for microcontroller data ingestion

#include <WiFi.h>
#include <WebSocketsClient.h>

const char* ssid = "OMNI_LAB_NETWORK";
const char* password = "OMNI_SECURE_WIFI";
const char* omni_server = "192.168.1.100";
const uint16_t omni_port = 8080;

WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("[OMNI Edge] Disconnected from engine.");
            break;
        case WStype_CONNECTED:
            Serial.println("[OMNI Edge] Connected to Universal Binary socket.");
            break;
        case WStype_TEXT:
            Serial.printf("[OMNI Edge] Instruction received: %s\n", payload);
            break;
    }
}

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while(WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n[OMNI Edge] WiFi Connected.");

    // Connect to the Omni Crystal/Go Websocket Router
    webSocket.begin(omni_server, omni_port, "/stream");
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);
}

void loop() {
    webSocket.loop();

    // Simulate reading a 3-axis accelerometer sensor 
    // This feeds directly into the GAMBA splat engine for physical state modeling
    static unsigned long lastUpdate = 0;
    if (millis() - lastUpdate > 100) { // 10Hz sampling
        lastUpdate = millis();
        
        float ax = random(-100, 100) / 100.0;
        float ay = random(-100, 100) / 100.0;
        float az = random(-100, 100) / 100.0;
        
        char payload[128];
        snprintf(payload, sizeof(payload), "{\"device\":\"esp32_edge_01\",\"ax\":%.3f,\"ay\":%.3f,\"az\":%.3f}", ax, ay, az);
        
        webSocket.sendTXT(payload);
    }
}
