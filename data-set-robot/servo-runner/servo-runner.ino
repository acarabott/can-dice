#include <Servo.h>

const uint8_t servoPin = 3;
const uint8_t shake_pos = 60;

Servo servo;

void setup() {
  pinMode(servoPin, OUTPUT);
  servo.attach(servoPin);
  servo.write(0);
  Serial.begin(115200);
}

void setServo(uint8_t value) {
  servo.write(constrain(value, 0, 270));
}

void shake() {
  setServo(shake_pos);
}


void roll() {
  setServo(0);
}


void loop() {
  shake();
  delay(1000);
  roll();
  delay(2000);
}
