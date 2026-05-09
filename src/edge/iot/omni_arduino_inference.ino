// Omni Microcontroller Inference (Arduino C++)
// IoT & Edge Layer
// Demonstrates running a heavily quantized (int8) Omni model 
// on constrained embedded devices (e.g. ESP32, Cortex-M4).

#include <Arduino.h>

// Simulated flat array of quantized weights
const int8_t omni_mini_weights[] = { 12, -4, 55, -120, 8, 0, 3, -19 };
const int num_weights = sizeof(omni_mini_weights) / sizeof(omni_mini_weights[0]);

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        ; // Wait for serial port to connect
    }
    Serial.println("Omni Edge Node Booting...");
    Serial.println("Loading quantized weights into SRAM.");
}

// Simple dot product simulating a single perceptron layer
int32_t compute_layer(const int8_t* inputs, const int8_t* weights, int length) {
    int32_t accumulator = 0;
    for (int i = 0; i < length; i++) {
        accumulator += inputs[i] * weights[i];
    }
    return accumulator;
}

void loop() {
    // Simulated sensor input (e.g. temperature, vibration)
    int8_t sensor_input[] = { 10, 20, -5, 100, 0, 5, 2, -10 };
    
    // Execute inference
    int32_t result = compute_layer(sensor_input, omni_mini_weights, num_weights);
    
    Serial.print("Inference Result (Raw Accumulator): ");
    Serial.println(result);
    
    // Simple activation logic
    if (result > 1000) {
        Serial.println("ANOMALY DETECTED. Triggering Omni Alert.");
    } else {
        Serial.println("Status Normal.");
    }
    
    delay(5000); // Wait 5 seconds before next inference
}
