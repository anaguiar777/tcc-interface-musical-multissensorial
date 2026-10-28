#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// ============================================================
// CONFIGURACAO DA REDE
// ============================================================

const char* WIFI_SSID = "SEU_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA";

const uint16_t UDP_PORT = 4210;

// ============================================================
// PINOS
// ============================================================

const int MOTOR_PIN = 18;
const int LED_PIN = 21;

// PWM de 8 bits: 0 a 255
const int PWM_FREQ = 5000;
const int PWM_RESOLUTION = 8;
const int MOTOR_CHANNEL = 0;
const int LED_CHANNEL = 1;

WiFiUDP udp;

void aplicarPWM(int pwm) {
  pwm = constrain(pwm, 0, 255);
  ledcWrite(MOTOR_CHANNEL, pwm);
  ledcWrite(LED_CHANNEL, pwm);
}

void processarComando(String comando) {
  comando.trim();

  if (comando == "OFF") {
    aplicarPWM(0);
    Serial.println("OFF");
    return;
  }

  if (comando.startsWith("ON,")) {
    int separador = comando.indexOf(',');
    int pwm = comando.substring(separador + 1).toInt();
    pwm = constrain(pwm, 0, 255);

    aplicarPWM(pwm);

    Serial.print("ON,");
    Serial.println(pwm);
  }
}

void conectarWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Conectando ao Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi conectado.");
  Serial.print("IP do ESP32: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);

  ledcSetup(MOTOR_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(LED_CHANNEL, PWM_FREQ, PWM_RESOLUTION);

  ledcAttachPin(MOTOR_PIN, MOTOR_CHANNEL);
  ledcAttachPin(LED_PIN, LED_CHANNEL);

  aplicarPWM(0);

  conectarWiFi();

  udp.begin(UDP_PORT);

  Serial.print("UDP ativo na porta ");
  Serial.println(UDP_PORT);
}

void loop() {
  int packetSize = udp.parsePacket();

  if (packetSize > 0) {
    char buffer[128];
    int len = udp.read(buffer, sizeof(buffer) - 1);

    if (len > 0) {
      buffer[len] = '\0';
      processarComando(String(buffer));
    }
  }

  // Se a rede cair, tenta reconectar.
  if (WiFi.status() != WL_CONNECTED) {
    aplicarPWM(0);
    conectarWiFi();
  }
}
