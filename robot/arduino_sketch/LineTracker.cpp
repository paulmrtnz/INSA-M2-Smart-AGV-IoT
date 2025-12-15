#include "LineTracker.h"

// Assuming: 0 = on line (black), 1 = off line (white)
#define WHITE 0
#define BLACK 1

LineTracker::LineTracker(int leftPin, int middlePin, int rightPin)
    : _leftPin(leftPin), _middlePin(middlePin), _rightPin(rightPin),
      _leftValue(0), _middleValue(0), _rightValue(0),
      _lostCounter(0) {}

void LineTracker::setup()
{
    pinMode(_leftPin, INPUT);
    pinMode(_middlePin, INPUT);
    pinMode(_rightPin, INPUT);
}

void LineTracker::readSensors()
{
    _leftValue = digitalRead(_leftPin);
    _middleValue = digitalRead(_middlePin);
    _rightValue = digitalRead(_rightPin);
}

LineCorrection LineTracker::getCorrection()
{
    readSensors();

    if (_middleValue == BLACK)
    {
        // Middle sensor is on the line - we're following correctly
        _lostCounter = 0; // Reset counter

        if (_leftValue == BLACK && _rightValue == WHITE)
        {
            // Left on line, right off line → turn left
            return LineCorrection::TURN_LEFT;
        }
        else if (_leftValue == WHITE && _rightValue == BLACK)
        {
            // Left off line, right on line → turn right
            return LineCorrection::TURN_RIGHT;
        }
        else
        {
            // Middle on line, go straight
            return LineCorrection::GO_STRAIGHT;
        }
    }
    else
    {
        // Middle sensor is NOT on the line - we've lost it
        if (_leftValue == BLACK && _rightValue == WHITE)
        {
            // Left on line, right off line → turn left
            _lostCounter = 0; // Reset counter
            return LineCorrection::TURN_LEFT;
        }
        else if (_leftValue == WHITE && _rightValue == BLACK)
        {
            // Left off line, right on line → turn right
            _lostCounter = 0; // Reset counter
            return LineCorrection::TURN_RIGHT;
        }
        else
        {
            // No sensor on the line → stop
            // return LineCorrection::STOP;
            /*
            _lostCounter++;
            if (_lostCounter <= 30)
            {
                return LineCorrection::ROTATE_LEFT;
            }
            else if (_lostCounter <= 60)
            {
                return LineCorrection::ROTATE_RIGHT;
            }
            else if (_lostCounter <= 100)
            {
                return LineCorrection::GO_BACKWARD;
            }
            else
            */
                return LineCorrection::STOP;
            
        }
    }
}
