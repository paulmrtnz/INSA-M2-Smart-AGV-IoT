#ifndef LINE_TRACKER_H
#define LINE_TRACKER_H

#include <Arduino.h>

// Defines the corrective action the robot should take based on line sensor readings
enum class LineCorrection {
    GO_STRAIGHT,
    TURN_LEFT,
    TURN_RIGHT,
    ROTATE_LEFT,
    ROTATE_RIGHT,
    GO_BACKWARD,
    STOP
};

class LineTracker {
public:
    LineTracker(int leftPin, int middlePin, int rightPin);
    void setup();
    LineCorrection getCorrection();

private:
    void readSensors();

    int _leftPin, _middlePin, _rightPin;
    int _leftValue, _middleValue, _rightValue;

    // State variables previously static in LT_decision
    int _lostCounter; 
};

#endif // LINE_TRACKER_H
