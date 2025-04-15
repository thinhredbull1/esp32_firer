#include <WiFi.h>
#include <WebSocketsClient.h>

WebSocketsClient webSocket;

// WiFi credentials
const char* ssid = "Thinh_wifi";
const char* password = "thinhdaica1";

uint8_t data[] = {0xff, 0xd8, 0xff}; // Example binary data (e.g., JPEG header)

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected!");

  webSocket.begin("172.20.10.2", 6789, "/"); // IP of your server
  webSocket.onEvent(webSocketEvent);
}

void webSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
  if (type == WStype_DISCONNECTED) {
    Serial.println("Disconnected!");
  } else if (type == WStype_CONNECTED) {
    Serial.println("Connected to WebSocket server!");
    webSocket.sendBIN(data, sizeof(data));  // Send binary data
  }
}

void loop() {
  webSocket.loop();
}
