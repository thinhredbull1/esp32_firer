#include <WiFi.h>
#include "esp_camera.h"
#include <WebSocketsClient.h>
#include <ESP32Servo.h>
WebSocketsClient webSocket;
#define use_serial 1
// WiFi credentials
const char *ssid = "Ngoi nha vui ve";
const char *password = "06011997";
#define MAX_LENGTH 50
#define RAD_TO_DEG 57.2957786
int timeSample = 500;
unsigned long time_d = 0;
bool start_camera = 0;
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22
camera_fb_t *fb = NULL;
int speed_desired;
float speed_increase;
bool run_ = 0;
unsigned long time_ = 0;
unsigned long time_stop;

#define tien 1
#define lui 2

#define BOM 4
#define BUZZ 0
#define mor_left 0
#define mor_right 1
#define STOP 0
#define DOWN 3
#define UP 1
#define LEFT 2
#define RIGHT 4
#define PI 3.14159265
int speed_left_get;
int speed_right_get;
const double WHEEL_DIAMTER = 5.2;
const double ENCODER_PULSE = 40;
const double cm_per_count = PI * WHEEL_DIAMTER / ENCODER_PULSE;
const double robot_with = 15;
double speed_linear = 0;
double speed_angular = 0;
int pwm[2] = { 14, 13 };
int dir[2] = { 15, 12 };
const int enc[] = { 2, 3 };
const int servo_pin = 1;
const int fire_sensor = 3;
bool fireSensorSignal = false;
int encoder_count[2] = { 0, 0 };
int speed_sign[2] = { 1, 1 };
Servo sv;
volatile bool connected = 0;
volatile bool fire_now = 0;
int angle_servo = 90;
int speed = 120;
bool PinStateChanged(int pin, int *lastButtonState, int *buttonRisingEdge) {

  int buttonState = pin;

  if (buttonState != *lastButtonState) {
    if (buttonState == LOW) {
      *buttonRisingEdge = 0;
    } else {
      *buttonRisingEdge = 1;
    }
    *lastButtonState = buttonState;
    return true;
  }

  return false;
}
void control_motor(int motor, int speed) {
  motor = 1 - motor;
  speed = -speed;
  if (motor == mor_right) speed = -speed;
  bool direct = speed > 0 ? 0 : 1;
  // digitalWrite(dir[motor],direct);
  // if(motor)

  if (speed == 0) {
    analogWrite(pwm[motor], 0);
    digitalWrite(dir[motor], 0);
    // speed_sign[motor]=0;
    return;
  }
  if (direct) {
    speed_sign[motor] = -1;
    analogWrite(pwm[motor], 255 - abs(speed));
    digitalWrite(dir[motor], 1);
  } else {
    speed_sign[motor] = 1;
    analogWrite(pwm[motor], abs(speed));
    digitalWrite(dir[motor], 0);
  }
}

void initGPIO() {
  if (!use_serial) {
    sv.attach(servo_pin, 500, 2400);
    sv.write(angle_servo);
    // pinMode(enc[mor_right], INPUT_PULLUP);
    pinMode(fire_sensor, INPUT);
  }
  // pinMode(fire_sensor,INPUT);
  pinMode(enc[mor_left], INPUT_PULLUP);
  pinMode(BOM, OUTPUT);
  digitalWrite(BOM, LOW);


  // pinMode(BUZZ, OUTPUT);
  // digitalWrite(BUZZ, 0);
  for (int i = 0; i < 2; i++) {

    pinMode(pwm[i], OUTPUT);
    pinMode(dir[i], OUTPUT);
    digitalWrite(pwm[i], LOW);
    digitalWrite(dir[i], LOW);
  }
}
void getEncoder() {
  bool enca_now = digitalRead(enc[mor_left]);

  static int buttonRisingEdgeA = 0;
  static int lastButtonStateA = 0;

  static unsigned long time_ = millis();
  if (PinStateChanged(enca_now, &lastButtonStateA, &buttonRisingEdgeA)) {

    // 0 == falling, 1 == Rising
    encoder_count[mor_left] += speed_sign[mor_left];
  }
  if (millis() - time_ >= timeSample) {

    // Serial.println(fireSensorSignal);
    double dxy = encoder_count[mor_left] * cm_per_count;
    float dt = (float)timeSample / 1000.0;
    speed_linear = ((dxy) / 2.0) / dt;
    speed_angular = (((encoder_count[mor_left]) * cm_per_count) / robot_with) / dt;
    int16_t linear_scaled = round(speed_linear * 100);
    int16_t angular_scaled = round(speed_angular * 570.2914);


    // Serial.print(speed_linear);
    // Serial.print(",");
    // Serial.println(encoder_count[mor_left]);
    // Serial.print(speed_left_get);
    // Serial.print(",");
    // Serial.println(speed_right_get);
    encoder_count[mor_right] = 0;
    encoder_count[mor_left] = 0;
    if (connected) {
      // uint8_t speed_data[8];
      // memcpy(speed_data, &speed_linear, 4);
      // memcpy(speed_data + 4, &speed_angular, 4);
      // webSocket.sendBIN(speed_data, 8);
      uint8_t speed_data[4];
      memcpy(speed_data, &linear_scaled, 2);
      memcpy(speed_data + 2, &angular_scaled, 2);

      webSocket.sendBIN(speed_data, 4);
    }
    time_ = millis();
  }
}

void onOffBOM(bool on) {
  if (on)
    analogWrite(BOM, 120);
  else
    analogWrite(BOM, 0);
}
void setup() {
  if (use_serial)
    Serial.begin(9600);
  initGPIO();
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  // init with high specs to pre-allocate larger buffers
  if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    // Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  s->set_framesize(s, FRAMESIZE_SVGA);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  // Serial.println("");

  // try to connect with Wifi network about 8 seconds
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    if (use_serial) Serial.print(".");
  }

  // Wait some time to connect to wifi

  if (use_serial) Serial.println(WiFi.localIP());  // You can get IP address assigned to ESP
  webSocket.begin("192.168.1.232", 6789, "/");     // IP of your server
  webSocket.onEvent(webSocketEvent);
}

void webSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
  if (type == WStype_DISCONNECTED) {
    connected = 0;
    // Serial.println("Disconnected!");
  } else if (type == WStype_CONNECTED) {
    // Serial.println("Connected to WebSocket server!");
    connected = 1;
    // webSocket.sendBIN(data, sizeof(data));  // Send binary data
  } else if (type == WStype_BIN) {
    // Serial.print("Received binary data of length: ");
    // Serial.println(length);
    for (size_t i = 0; i < length; i++) {
      // Serial.printf("0x%02x ", payload[i]);
    }
    // Serial.println();
  } else if (type == WStype_TEXT) {
    // Serial.printf("[WSc] get text: %s\n", payload);
    String command = String((char *)payload);
    int p_index = command.indexOf("p");
    if (p_index != -1) {
      int state_on = command.substring(0, p_index).toInt();
      if (state_on == 0) {
        static int onOf = 1;
        onOffBOM(onOf);
        onOf = 1 - onOf;
      } else if (state_on == 1) {
        fire_now = 1;
      }
    }
    int servo_index = command.indexOf("s");
    if (servo_index != -1) {
      int sv_dir = command.substring(0, servo_index).toInt();
      if (sv_dir == 1)
        angle_servo += 5;
      else
        angle_servo -= 5;
      angle_servo = constrain(angle_servo, 0, 180);
      if (!use_serial) sv.write(angle_servo);
      // Serial.println(angle_servo);
    }
    int ind_move = command.indexOf("k");
    if (ind_move != -1) {
      int speed_left = command.substring(0, ind_move).toInt();
      int speed_right = command.substring(ind_move + 1).toInt();
      // moveRobot(index);
      if (fire_now && fireSensorSignal) {
        speed_left = constrain(speed_left, -75, 75);
        speed_right = constrain(speed_right, -75, 75);
      }

      control_motor(mor_right, speed_right);
      control_motor(mor_left, speed_left);
      // Serial.println(index);
    }
  }
}
void loop() {
  // if (Serial.available()) {
  //   String c = Serial.readStringUntil(';');
  //   int ind_move = c.indexOf("k");
  //   if (ind_move != -1) {
  //     int speed_left = c.substring(0, ind_move).toInt();
  //     int speed_right = c.substring(ind_move + 1).toInt();
  //     // moveRobot(index);
  //     if (fire_now && fireSensorSignal) {
  //       speed_left = constrain(speed_left, -75, 75);
  //       speed_right = constrain(speed_right, -75, 75);
  //     }
  //     control_motor(mor_right, speed_right);
  //     control_motor(mor_left, speed_left);
  //     Serial.print(speed_right);
  //     Serial.print("m");
  //     Serial.println(speed_left);
  //   }
  // }
  if (!use_serial) fireSensorSignal = digitalRead(fire_sensor);
  webSocket.loop();


  if (millis() - time_d > 100) {  // 100ms =0.1s
    // unsigned long time_=millis();
    if (connected) {
      //   onOffBuzz();
      fb = esp_camera_fb_get();
      // client.sendBinary((const char*)fb->buf, fb->len);
      webSocket.sendBIN(fb->buf, fb->len);
      esp_camera_fb_return(fb);
      fb = NULL;
    }
    time_d = millis();
    // Serial.println(millis()-time_); // 37-78
  }
  getEncoder();
}