// OMNI Robotics Layer
// Arduino C interface for translating Omni Reinforcement Learning (RL) continuous outputs
// into physical servo/motor actuations for Humanoid Locomotion (HLT).

#include <Servo.h>

#define NUM_SERVOS 6

Servo joints[NUM_SERVOS];
int servoPins[NUM_SERVOS] = {2, 3, 4, 5, 6, 7};

// The Omni Universal Binary communicates continuous policy outputs over serial
// We must map these floats [-1.0, 1.0] to PWM ranges [0, 180]

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(10); // Low latency reads for realtime control
    
    for(int i = 0; i < NUM_SERVOS; i++) {
        joints[i].attach(servoPins[i]);
        joints[i].write(90); // Initialize to resting state
    }
    
    Serial.println("OMNI Actuator Controller: Initialization Complete. Awaiting Policy Commands.");
}

void loop() {
    // Expecting comma-separated floats from the Omni Go HLT Engine
    // Format: -0.50,1.00,0.00,-0.25,0.80,0.10\n
    if (Serial.available() > 0) {
        String payload = Serial.readStringUntil('\n');
        parseAndActuate(payload);
    }
}

void parseAndActuate(String payload) {
    int servoIndex = 0;
    int strIndex = 0;
    
    while (strIndex < payload.length() && servoIndex < NUM_SERVOS) {
        int nextComma = payload.indexOf(',', strIndex);
        if (nextComma == -1) nextComma = payload.length();
        
        String valStr = payload.substring(strIndex, nextComma);
        float actionValue = valStr.toFloat(); // [-1.0 to 1.0]
        
        // Map policy output to servo degrees safely
        int targetAngle = mapPolicyToDegrees(actionValue);
        joints[servoIndex].write(targetAngle);
        
        strIndex = nextComma + 1;
        servoIndex++;
    }
}

int mapPolicyToDegrees(float action) {
    // Constrain to physical limits to prevent hardware damage
    action = constrain(action, -1.0, 1.0);
    return (int)((action + 1.0) * 90.0); // Maps -1..1 to 0..180
}
