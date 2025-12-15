#ifndef ULTRASONIC_SENSOR_H
#define ULTRASONIC_SENSOR_H

#include <Arduino.h>

class UltrasonicSensor {
public:
    UltrasonicSensor(int trigPin, int echoPin);
    void setup();
    // Returns distance in cm, or -1 if timeout
    float readDistance(); 

private:
    int _trigPin;
    int _echoPin;
};

#endif // ULTRASONIC_SENSOR_H
