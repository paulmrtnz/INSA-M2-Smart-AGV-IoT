#ifndef MOTOR_CONTROLLER_H
#define MOTOR_CONTROLLER_H

#include <Arduino.h>

class MotorController {
public:
    MotorController();
    void setup();
    void setSpeed(int speed);
    int getCurrentSpeed() const;
    void moveForward();
    void moveBackward();
    void turnLeft();
    void rotateLeft();
    void turnRight();
    void rotateRight();
    void stop();

private:
    void setMotor(char motor, bool direction, int speed);
    int _currentSpeed;

    // Pin definitions are kept internal
    static const int ML_Ctrl = 4; //ok
    static const int ML_PWM = 6; //ok
    static const int MR_Ctrl = 2; //ok
    static const int MR_PWM = 5; //ok
};

#endif // MOTOR_CONTROLLER_H
