#ifndef PHOTORESISTOR_H
#define PHOTORESISTOR_H

#include <Arduino.h>

class Photoresistor {
public:
    Photoresistor(int pin);
    void setup();
    int readLightLevel();

private:
    int _pin;
};

#endif // PHOTORESISTOR_H
