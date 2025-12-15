#include "Photoresistor.h"

Photoresistor::Photoresistor(int pin) : _pin(pin) {
}

void Photoresistor::setup() {
    pinMode(_pin, INPUT);
}

int Photoresistor::readLightLevel() {
    return analogRead(_pin);
}