#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// WiFi credentials
const char* ssid = "POCO F3 GT";
const char* pass = "84218421";

// DHT sensor config
#define DHTPIN D4
DHT dht(DHTPIN, DHT11);

// Soil sensor
const int soilMoisturePin = A0;

// Fan
const int fanRelayPin = D1;
const float temperatureThreshold = 32.0;
int fanStatus = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(fanRelayPin, OUTPUT);
  digitalWrite(fanRelayPin, LOW);

  WiFi.begin(ssid, pass);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
  } else {
    Serial.println("\nWiFi not connected");
  }
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int soilMoistureValue = analogRead(soilMoisturePin);

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Fan control logic
  if (temperature > temperatureThreshold) {
    digitalWrite(fanRelayPin, LOW);
    fanStatus = 1;
  } else {
    digitalWrite(fanRelayPin, HIGH);
    fanStatus = 0;
  }

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, "http://10.38.138.242:5000/iot-data");  // Replace with your PC's IP
    http.addHeader("Content-Type", "application/json");

    String jsonData = "{";
    jsonData += "\"temperature\":" + String(temperature, 2) + ",";
    jsonData += "\"humidity\":" + String(humidity, 2) + ",";
    jsonData += "\"soil_moisture\":" + String(soilMoistureValue) + ",";
    jsonData += "\"fan_status\":" + String(fanStatus);
    jsonData += "}";

    int httpCode = http.POST(jsonData);
    Serial.println("POST response code: " + String(httpCode));
    http.end();
  }

  delay(15000); // Same as ThingSpeak free tier
}
