#ifndef ROBOT_H
#define ROBOT_H

#include "MotorController.h"
#include "UltrasonicSensor.h"
#include "LineTracker.h"
#include "IRRemote.h"
#include "Photoresistor.h"
#include "LEDMatrix.h"
#include "MetricsManager.h"
#include "BluetoothManager.h"

// Defines the main operational states of the robot
enum class RobotState {
    STARTING,
    WAITING_BT,
    MANUAL,
    AUTO,
    OBSTACLE_DETECTED
};

class Robot {
public:
    Robot();
    void setup();
    void loop();

private:
    // --- State Management ---
    void changeState(RobotState newState);
    void handleState();
    void handleWaitingBtState();
    void handleManualState();
    void handleAutoState();
    void handleObstacleDetectedState();

    // --- Core Tasks ---
    void checkSensors();
    void updateMetrics();
    void sendTelemetryIfNeeded();

    // --- Component Objects ---
    MotorController _motors;
    UltrasonicSensor _usSensor;
    LineTracker _lineTracker;
    IRRemote _irRemote;
    Photoresistor _photoresistor;
    LEDMatrix _ledMatrix;
    MetricsManager _metricsManager;
    BluetoothManager _btManager;

    // --- Robot State & Timers ---
    RobotState _currentState;
    float _lastDistance;
    int _lastLightLevel;
    unsigned long _lastIrCommand;
    unsigned long _lastIrTime;
    bool _headlightsOn;
    unsigned long _ledBlinkTimer;
    unsigned long _obstacleCheckTimer;
    unsigned long _btWaitingDisplayTimer;

    // Timers for non-blocking operations
    unsigned long _telemetryTimer;
    unsigned long _cumulativeMetricsTimer;
    unsigned long _sensorCheckTimer;
};

#endif // ROBOT_H
