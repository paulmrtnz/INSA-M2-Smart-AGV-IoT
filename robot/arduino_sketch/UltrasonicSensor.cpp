#include "UltrasonicSensor.h"

UltrasonicSensor::UltrasonicSensor(int trigPin, int echoPin) : _trigPin(trigPin), _echoPin(echoPin) {}

void UltrasonicSensor::setup() {
    pinMode(_trigPin, OUTPUT);
    pinMode(_echoPin, INPUT);
}

float UltrasonicSensor::readDistance() {
    // Generate a 10us pulse to trigger the sensor.
    digitalWrite(_trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(_trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(_trigPin, LOW);

    // Read the pulse duration from the echo pin.
    // pulseIn returns the pulse duration in microseconds or 0 if no pulse is completed before the timeout.
    long duration = pulseIn(_echoPin, HIGH);

    // Convert the duration to distance in centimeters.
    // The formula is based on the speed of sound.
    // (duration / 2) is the time for one way travel.
    // 29.1 is the microseconds it takes for sound to travel 1 cm.
    if (duration > 0) {
        return static_cast<float>(duration) / 2.0 / 29.1;
    } else {
        return -1.0; // Indicate a timeout or error
    }
}
