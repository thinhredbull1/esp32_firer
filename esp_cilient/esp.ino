#include <WiFi.h>
#include <SocketIoClient.h>
#include <Base64.h>  // Thư viện để mã hóa base64
/////////////////////////////////////
////// USER DEFINED VARIABLES //////
///////////////////////////////////
// WIFI Settings
const char* ssid = "MKAC";
const char* password = "MKAC12345";

// Socket.IO Settings
char host[] = "192.168.0.92";                     // Socket.IO Server Address
int port = 5000;                                  // Socket.IO Port Address
char path[] = "/socket.io/?transport=websocket";  // Socket.IO Base Path
bool useSSL = false;                              // Use SSL Authentication
const char* sslFingerprint = "";                  // SSL Certificate Fingerprint
bool useAuth = false;                             // use Socket.IO Authentication
const char* serverUsername = "socketIOUsername";
const char* serverPassword = "socketIOPassword";

// Pin Settings
int LEDPin = 2;
int buttonPin = 0;

/////////////////////////////////////
////// ESP32 Socket.IO Client //////
///////////////////////////////////

SocketIoClient webSocket;
WiFiClient client;

bool LEDState = false;

// Create a fixed byte array of 1024 bytes
uint8_t imageByte[] = {
  0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
  0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0xFF, 0xB7, 0xC8, 0xE9, 0xC8, 0xA7, 0xFF,
  0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
  0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0xFF, 0xB7, 0xC8, 0xE9, 0xC8, 0xA7, 0xFF,
  0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
  0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0xFF, 0xB7, 0xC8, 0xE9, 0xC8, 0xA7, 0xFF,
  0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
  0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43, 0x00, 0xFF, 0xB7, 0xC8, 0xE9, 0xC8, 0xA7, 0xFF,
  // Add more bytes here to reach 1024 bytes total
  // (In practice, you would likely fill in more actual data or just use placeholders for testing)
  0xFF, 0xE9, 0xD9, 0xE9, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
  0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
  // More placeholder or sample bytes...
  0xFF, 0xD9  // Ending byte
};

void socket_Connected(const char* payload, size_t length) {
  Serial.println("Socket.IO Connected!");
}

void socket_event(const char* payload, size_t length) {
  Serial.print("Received message: ");
  Serial.println(payload);
}

void socket_sendImage() {
  // Send the image byte array as binary data
  char base64Data[2048];  // Đảm bảo mảng có đủ dung lượng
  int imageLength = sizeof(imageByte);
  Base64.encode(base64Data, (char*)imageByte, imageLength);
  // Send the base64-encoded image as a string
  String jsonData = "{\"image_frame\": \"" + String(base64Data) + "\"}";

  // Send the JSON data to the server
  webSocket.emit("image_frame", jsonData.c_str());
}

void setup() {
  Serial.begin(115200);
  delay(10);

  pinMode(LEDPin, OUTPUT);
  pinMode(buttonPin, INPUT);

  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  // Setup 'on' listen events
  webSocket.on("connect", socket_Connected);
  webSocket.on("event", socket_event);

  // Setup Connection
  if (useSSL) {
    webSocket.beginSSL(host, port, path, sslFingerprint);
  } else {
    webSocket.begin(host, port, path);
  }

  // Handle Authentication
  if (useAuth) {
    webSocket.setAuthorization(serverUsername, serverPassword);
  }
}

void loop() {
  webSocket.loop();
  static unsigned long time_ = millis();
  if (millis() - time_ > 1500) {  // Call this function when needed to send the image byte
    socket_sendImage();
    time_ = millis();
  }
}
