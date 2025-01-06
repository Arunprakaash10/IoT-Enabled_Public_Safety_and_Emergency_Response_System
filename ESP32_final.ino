#include <WiFi.h>
#include <HTTPClient.h>

// Define sensor pins
#define PIR_PIN 13       // GPIO 13 for the PIR sensor
#define DHT_PIN 15       // GPIO 15 for the DHT11 sensor
#define PHOTO_PIN 34     // GPIO 34 for the light sensor (analog)
#define MQ2_PIN 35       // GPIO 35 for the smoke sensor (analog)
#define BUTTON_PIN 4     // GPIO 4 for the panic button
#define LED_PIN 33       // GPIO 33 for the LED (PWM pin for controlling brightness)

// Wi-Fi credentials
const char* ssid = "V2031";  
const char* password = "arun2004";

// Flask API endpoint (replace with your server's IP and port)
const String api_url = "http://34.47.189.84:5000/sensor_data";

// Variables to hold sensor data
float temperature, humidity;  // Placeholder values for DHT (can integrate DHT11/22 later)
int lightLevel, smokeLevel;
bool motionDetected, panicPressed;

// Timing variables for non-blocking delay
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 3000; // 3 seconds

void setup() {
  Serial.begin(115200);

  // Initialize sensor pins
  pinMode(PIR_PIN, INPUT);
  pinMode(PHOTO_PIN, INPUT);
  pinMode(MQ2_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // Use internal pull-up resistor
  pinMode(LED_PIN, OUTPUT);           // LED pin as output for PWM control

  // Connect to Wi-Fi
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {  // Timeout after 30 seconds
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnected to WiFi");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi. Check credentials and network.");
  }
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - lastSendTime >= sendInterval) {
    lastSendTime = currentTime;

    // Read sensors, adjust brightness, and send data
    readSensors();
    adjustLightBrightness();
    sendDataToServer();
  }
}

void readSensors() {
  // Simulated temperature and humidity values
  temperature = random(200, 350) / 10.0; // Generate random temperature between 20.0°C and 35.0°C
  humidity = random(300, 700) / 10.0;    // Generate random humidity between 30.0% and 70.0%

  // PIR motion detection
  motionDetected = digitalRead(PIR_PIN);

  // Light level (LDR sensor reading)
  lightLevel = analogRead(PHOTO_PIN);

  // Smoke level
  smokeLevel = analogRead(MQ2_PIN);

  // Panic button state
  panicPressed = !digitalRead(BUTTON_PIN);  // Button is pressed when LOW due to pull-up

  // Log sensor data
  Serial.println("Sensor Readings:");
  Serial.print("Temperature: "); Serial.println(temperature);
  Serial.print("Humidity: "); Serial.println(humidity);
  Serial.print("Motion Detected: "); Serial.println(motionDetected ? "Yes" : "No");
  Serial.print("Light Level: "); Serial.println(lightLevel);
  Serial.print("Smoke Level: "); Serial.println(smokeLevel);
  Serial.print("Panic Button Pressed: "); Serial.println(panicPressed ? "Yes" : "No");
  Serial.println();
}

void adjustLightBrightness() {
  // Map the LDR reading (0-4095) to PWM range (0-255)
  int brightness = map(lightLevel, 0, 4095, 255, 0);  // Inverse because higher LDR value means brighter ambient light

  // Set the LED brightness using PWM
  analogWrite(LED_PIN, brightness);

  // Log the adjustment for debugging
  Serial.print("LED Brightness (mapped from LDR): ");
  Serial.println(brightness);
}

void sendDataToServer() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Specify the URL for the Flask API endpoint
    http.begin(api_url);
    http.addHeader("Content-Type", "application/json");  // Set content type to JSON

    // Create the JSON payload
    String jsonPayload = "{\"temperature\": " + String(temperature) + 
                          ", \"humidity\": " + String(humidity) + 
                          ", \"light_level\": " + String(lightLevel) + 
                          ", \"smoke_level\": " + String(smokeLevel) + 
                          ", \"motion_detected\": " + (motionDetected ? "true" : "false") + 
                          ", \"panic_pressed\": " + (panicPressed ? "true" : "false") + "}";

    // Send the POST request
    int httpResponseCode = http.POST(jsonPayload);

    // Check the response
    if (httpResponseCode > 0) {
      Serial.println("Data sent successfully.");
      Serial.println("HTTP Response Code: " + String(httpResponseCode));
    } else {
      Serial.println("Error in sending data.");
      Serial.println("HTTP Response Code: " + String(httpResponseCode));
    }
    Serial.print("\n");

    http.end();  // Free resources
  } else {
    Serial.println("WiFi not connected!");
  }
}