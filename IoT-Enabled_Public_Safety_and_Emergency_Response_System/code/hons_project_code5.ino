#include "DHT.h"

// Pin Definitions
const int mq2Pin = A0;         // MQ-2 gas sensor analog pin
const int dhtPin = 2;          // DHT11 sensor digital pin
const int pirPin = 7;          // HC-SR501 PIR sensor digital pin
const int ldrPin = A1;         // LDR sensor analog pin
const int ledPin = 13;         // LED for motion and light detection (optional)

// DHT11 settings
#define DHTTYPE DHT11
DHT dht(dhtPin, DHTTYPE);

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Set PIR pin and LED pin as input and output respectively
  pinMode(pirPin, INPUT);
  pinMode(ledPin, OUTPUT);

  // Provide instructions to the user
  Serial.println("IoT Sensor Values Display:");
  Serial.println("Monitoring Gas, Temperature, Humidity, Motion, and Light...");
}

void loop() {
  // MQ-2 Gas Sensor Readings
  int gasValue = analogRead(mq2Pin);
  
  // DHT11 Temperature and Humidity Sensor Readings
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  // PIR Motion Sensor Readings
  int motionDetected = digitalRead(pirPin);

  // LDR Sensor Readings
  int ldrValue = analogRead(ldrPin);

  // Display sensor values in a simulated output format
  Serial.print("MQ-2 Gas Value: ");
  Serial.println(gasValue);

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.print(" %\tTemperature: ");
  Serial.print(temperature);
  Serial.println(" *C");

  Serial.print("Motion: ");
  Serial.println(motionDetected == HIGH ? "Detected" : "Not Detected");

  Serial.print("Simulated LDR Value: ");
  Serial.println(ldrValue);

  // Leave a line in Serial Monitor after each iteration
  Serial.println();  // Line break

  // Delay for 2 seconds between readings
  delay(2000);
}
