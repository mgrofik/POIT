// - DHT Sensor Library: https://github.com/adafruit/DHT-sensor-library
// - Adafruit Unified Sensor Lib: https://github.com/adafruit/Adafruit_Sensor
#include <Wire.h>
#include <Adafruit_BMP085.h>
#include "DHT.h"

#define seaLevelPressure_hPa 1013.25
#define DHTPIN 4     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22  

// Initialize DHT and bmp sensor.

DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP085 bmp;

void setup() {
  Serial.begin(9600);
  //Serial.println(F("DHTxx test!"));
  dht.begin();
  bmp.begin();
}

void loop() {
  // Wait a 2 seconds between measurements.
  delay(2000);
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);

  //Serial.print(F("Humidity: "));
  Serial.println(h);
 // Serial.print(" ");
 // Serial.print(F("%  Temperature: "));
  Serial.println(t);
  //Serial.print("Pressure = ");
  Serial.println(bmp.readPressure());
   // Serial.println(" Pa");
  
}
