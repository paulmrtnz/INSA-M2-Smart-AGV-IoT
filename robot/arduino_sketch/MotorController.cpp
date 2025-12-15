#include "MotorController.h"

MotorController::MotorController() : _currentSpeed(0) {}

void MotorController::setup() {
    pinMode(ML_Ctrl, OUTPUT);
    pinMode(ML_PWM, OUTPUT);
    pinMode(MR_Ctrl, OUTPUT);
    pinMode(MR_PWM, OUTPUT);
    stop();
}

void MotorController::setSpeed(int speed) {
    if (speed < 0) speed = 0;
    if (speed > 255) speed = 255;
    _currentSpeed = speed;
}

int MotorController::getCurrentSpeed() const {
    return _currentSpeed;
}

void MotorController::setMotor(char motor, bool direction, int speed) {
    if (motor == 'L') {
        digitalWrite(ML_Ctrl, direction);
        analogWrite(ML_PWM, speed);
    } else if (motor == 'R') {
        digitalWrite(MR_Ctrl, direction);
        analogWrite(MR_PWM, speed);
    }
}

void MotorController::moveForward() {
    setMotor('L', HIGH, _currentSpeed);
    setMotor('R', HIGH, _currentSpeed);
}

void MotorController::moveBackward() {
    setMotor('L', LOW, 80);
    setMotor('R', LOW, 80);
}

void MotorController::turnLeft() {
    setMotor('L', LOW, 0);
    setMotor('R', HIGH, _currentSpeed);
}

void MotorController::rotateLeft() {
    setMotor('L', LOW, _currentSpeed);
    setMotor('R', HIGH, _currentSpeed);
}

void MotorController::turnRight() {
    setMotor('L', HIGH, _currentSpeed);
    setMotor('R', LOW, 0);
}

void MotorController::rotateRight() {
    setMotor('L', HIGH, _currentSpeed);
    setMotor('R', LOW, _currentSpeed);
}

void MotorController::stop() {
    setMotor('L', LOW, 0);
    setMotor('R', LOW, 0);
    _currentSpeed = 0;
}
