#include <WiFi.h>
#include <HTTPClient.h>

// ====== Wi-Fi ======
const char* WIFI_SSID = "Sergio's Galaxy S23 ultra";   // 2.4 GHz
const char* WIFI_PASS = "123456789";

// ====== Servidor Flask (laptop) ======
const char* LAPTOP_IP = "172.19.123.152";     // IP local laptop
const uint16_t HTTP_PORT = 5000;
const char* HTTP_PATH = "/ingest";

// ====== Sensor 4–20 mA vía shunt ======
const int   SENSOR_PIN = 34;                  // ADC1_CH6 (solo-entrada)
const int   NUM_AVG    = 1000;                // Promedio anti-ruido
const float R_SHUNT    = 150.0f;              // Ω

// ====== Conexión Wi-Fi con reintento ======
void waitForWiFi() {
  Serial.print("Conectando al Wi-Fi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  uint32_t t0 = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (millis() - t0 > 15000) { // 15 s
      Serial.println("\nReintentando Wi-Fi...");
      WiFi.disconnect(true, true);
      delay(800);
      WiFi.begin(WIFI_SSID, WIFI_PASS);
      t0 = millis();
    }
  }
  Serial.println("\nConectado al Wi-Fi");
  Serial.print("IP del ESP32: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  delay(800);

  analogReadResolution(12);                       // 0..4095
  analogSetPinAttenuation(SENSOR_PIN, ADC_11db);  // hasta ~3.3 V

  waitForWiFi();
}

void loop() {
  // --- Lectura promedio en mV ---
  long sum_mV = 0;
  for (int i = 0; i < NUM_AVG; i++) {
    sum_mV += analogReadMilliVolts(SENSOR_PIN);
  }
  const float v_shunt = (sum_mV / (float)NUM_AVG) / 1000.0f; // Voltios

  // --- 4–20 mA → % ---
  const float i_mA = (v_shunt / R_SHUNT) * 1000.0f;          // I=V/R → mA
  float pct = (i_mA - 4.0f) * (100.0f / 16.0f);              // 4..20 mA → 0..100
  if (pct < 0)   pct = 0;
  if (pct > 100) pct = 100;

  String json = "{\"v\":" + String(v_shunt, 3) + ",\"pct\":" + String(pct, 2) + "}";

  if (WiFi.status() != WL_CONNECTED) waitForWiFi();

  HTTPClient http;
  String url = "http://" + String(LAPTOP_IP) + ":" + String(HTTP_PORT) + HTTP_PATH;
  Serial.print("POST -> "); Serial.println(url);
  http.setTimeout(7000);
  if (!http.begin(url)) {
    Serial.println("http.begin() falló");
    delay(10000);
    return;
  }
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(json);
  Serial.printf("HTTP code = %d (%s)\n", code, HTTPClient::errorToString(code).c_str());
  if (code > 0) {
    String body = http.getString();
    Serial.print("Respuesta: "); Serial.println(body);
  }
  http.end();

  delay(10000); // cada 10 s
}

