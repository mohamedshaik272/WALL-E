// Pin Definitions
const int motorA_dirPin = 12;
const int motorA_brakePin = 9;
const int motorA_speedPin = 3;
const int motorB_dirPin = 13;
const int motorB_brakePin = 8;
const int motorB_speedPin = 11;

// Motor Control Functions
void setMotorSpeed(int dirPin, int brakePin, int speedPin, int dir, int speed) {
  digitalWrite(dirPin, dir); // Set direction
  digitalWrite(brakePin, LOW); // Disengage the brake
  analogWrite(speedPin, speed); // Set motor speed
}

void stopMotor(int brakePin) {
  digitalWrite(brakePin, HIGH); // Engage the brake
}

// Combined Movement Functions
void forward(int speed) {
  setMotorSpeed(motorA_dirPin, motorA_brakePin, motorA_speedPin, LOW, speed);
  setMotorSpeed(motorB_dirPin, motorB_brakePin, motorB_speedPin, LOW, speed);
}

void backward(int speed) {
  setMotorSpeed(motorA_dirPin, motorA_brakePin, motorA_speedPin, HIGH, speed);
  setMotorSpeed(motorB_dirPin, motorB_brakePin, motorB_speedPin, HIGH, speed);
}

void turnRight(int speed) {
  setMotorSpeed(motorA_dirPin, motorA_brakePin, motorA_speedPin, LOW, speed);
  setMotorSpeed(motorB_dirPin, motorB_brakePin, motorB_speedPin, HIGH, speed);
}

void turnLeft(int speed) {
  setMotorSpeed(motorA_dirPin, motorA_brakePin, motorA_speedPin, HIGH, speed);
  setMotorSpeed(motorB_dirPin, motorB_brakePin, motorB_speedPin, LOW, speed);
}

void stopAll() {
  stopMotor(motorA_brakePin);
  stopMotor(motorB_brakePin);
}

void setup() {
  // Set all motor pins to output mode
  int pins[] = {motorA_dirPin, motorA_brakePin, motorB_dirPin, motorB_brakePin};
  for (int i = 0; i < 4; i++) {
    pinMode(pins[i], OUTPUT);
  }
  Serial.begin(9600); // Start serial communication
}

void loop() {
  if (Serial.available()) {
    char receivedData = Serial.read();
    switch (receivedData) {
      case 'f':
        Serial.println("Moving Forward and Back");
        forward(255);  // Highest speed forward
        delay(30000);  // Move forward for 30 seconds
        stopAll();
        delay(1000);   // 1 second pause
        backward(200); // Slower backward speed
        delay(30000);  // Move backward for 30 seconds
        stopAll();
        Serial.println("Returned to starting position");
        break;
      case 'r':
        Serial.println("Moving Right and Back");
        forward(255);  // Highest speed forward
        delay(10000);  // Move forward for 10 seconds
        stopAll();
        delay(1000);   // 1 second pause
        turnRight(200);
        delay(15000);  // Turn right for 15 seconds
        stopAll();
        delay(1000);   // 1 second pause
        forward(255);  // Highest speed forward
        delay(10000);  // Move forward for 10 seconds
        stopAll();
        delay(1000);   // 1 second pause
        // Return to starting position
        backward(200); // Slower backward speed
        delay(10000);  // Move backward for 10 seconds
        stopAll();
        delay(1000);   // 1 second pause
        turnLeft(200);
        delay(15000);  // Turn left for 15 seconds
        stopAll();
        delay(1000);   // 1 second pause
        backward(200); // Slower backward speed
        delay(10000);  // Move backward for 10 seconds
        stopAll();
        Serial.println("Returned to starting position");
        break;
      case 'l':
        Serial.println("Moving Left and Back");
        forward(255);  // Highest speed forward
        delay(10000);  // Move forward for 10 seconds
        stopAll();
        delay(1000);   // 1 second pause
        turnLeft(200);
        delay(15000);  // Turn left for 15 seconds
        stopAll();
        delay(1000);   // 1 second pause
        forward(255);  // Highest speed forward
        delay(10000);  // Move forward for 10 seconds
        stopAll();
        delay(1000);   // 1 second pause
        // Return to starting position
        backward(200); // Slower backward speed
        delay(10000);  // Move backward for 10 seconds
        stopAll();
        delay(1000);   // 1 second pause
        turnRight(200);
        delay(15000);  // Turn right for 15 seconds
        stopAll();
        delay(1000);   // 1 second pause
        backward(200); // Slower backward speed
        delay(10000);  // Move backward for 10 seconds
        stopAll();
        Serial.println("Returned to starting position");
        break;
      case 's':
        stopAll();
        Serial.println("Stopped");
        break;
      default:
        Serial.println("Invalid command");
        break;
    }
  }
}