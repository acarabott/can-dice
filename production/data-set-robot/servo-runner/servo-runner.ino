#include <Servo.h>

const uint8_t servoPin = 3;
const uint8_t shake_pos = 80;

uint16_t wait = 500;

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
  if (Serial.available() > 0) {
    const auto read = Serial.parseInt();
    wait = read;
    Serial.print("setting wait to ");
    Serial.println(wait);
  }
  shake();
  delay(wait);
  roll();
  delay(2000);
}
