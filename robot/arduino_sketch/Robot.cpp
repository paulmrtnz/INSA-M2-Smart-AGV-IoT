#include "Robot.h"

// --- Pin Definitions ---

const int WARNING_LED = A1; // ok
const int PHOTORESISTOR_PIN = A2; //ok
const int MATRIX_SDA_PIN = A4; //ok
const int MATRIX_SCL_PIN = A5; //ok

const int IR_RECV_PIN = 3; //ok
const int LINE_MIDDLE_PIN = 7; //ok
const int LINE_RIGHT_PIN = 8; //ok
const int LINE_LEFT_PIN = 11; //ok
const int ULTRASONIC_TRIG_PIN = 12; //ok
const int ULTRASONIC_ECHO_PIN = 13; //ok

// --- Constants ---
const long TELEMETRY_INTERVAL = 30000; // 30 seconds
const long SENSOR_CHECK_INTERVAL = 100;
const long CUMULATIVE_METRICS_INTERVAL = 20;
const int OBSTACLE_DISTANCE_THRESHOLD = 25; // in cm
const unsigned long IR_TIMEOUT = 150; // ms to forget last IR command
const int LIGHT_THRESHOLD = 400; // Light level threshold for headlights
const unsigned long LED_BLINK_INTERVAL = 200; // LED blink period in ms
const unsigned long OBSTACLE_CHECK_INTERVAL = 500; // Check obstacle every 500ms
const unsigned long BT_BAUDRATE = 9600; // Baud rate for Bluetooth module

// IR Remote Codes
const unsigned long IR_CMD_AUTO_MODE = 0xFF52AD; // #
const unsigned long IR_CMD_MANUAL_MODE = 0xFF42BD; // *
const unsigned long IR_CMD_FORWARD = 0xFF629D; // Arrow Up
const unsigned long IR_CMD_BACKWARD = 0xFFA857; // Arrow Down
const unsigned long IR_CMD_TURN_LEFT = 0xFF22DD; // Arrow Left
const unsigned long IR_CMD_TURN_RIGHT = 0xFFC23D; // Arrow Right
const unsigned long IR_CMD_STOP = 0xFF02FD; // OK
const unsigned long IR_CMD_ROT_LEFT = 0xFF30CF; // 4
const unsigned long IR_CMD_ROT_RIGHT = 0xFF7A85; // 6
const unsigned long IR_CMD_LIGHTS_ON = 0xFFE21D; // 1
const unsigned long IR_CMD_LIGHTS_OFF = 0xFF926D; // 2



Robot::Robot() :
    _motors(),
    _usSensor(ULTRASONIC_TRIG_PIN, ULTRASONIC_ECHO_PIN),
    _lineTracker(LINE_LEFT_PIN, LINE_MIDDLE_PIN, LINE_RIGHT_PIN),
    _irRemote(IR_RECV_PIN),
    _photoresistor(PHOTORESISTOR_PIN),
    _ledMatrix(MATRIX_SCL_PIN, MATRIX_SDA_PIN),
    _metricsManager(_motors),
    _btManager(),
    _currentState(RobotState::STARTING),
    _lastDistance(0.0),
    _lastLightLevel(0),
    _lastIrCommand(0),
    _lastIrTime(0),
    _headlightsOn(false),
    _ledBlinkTimer(0),
    _obstacleCheckTimer(0),
    _btWaitingDisplayTimer(0),
    _telemetryTimer(0),
    _cumulativeMetricsTimer(0),
    _sensorCheckTimer(0)
{}

void Robot::setup() {
    _ledMatrix.setup();
    _ledMatrix.displayPattern(LEDMatrix::PGPLogo);
    _motors.setup();
    _usSensor.setup();
    _lineTracker.setup();
    _irRemote.setup();
    _photoresistor.setup();
    _metricsManager.setup();
    _btManager.setup(9600);

    delay(2000); // Display logo for 2 seconds
    _ledMatrix.clear();
    _ledMatrix.scrollTextBlocking("Robot Start", 50);
    
    changeState(RobotState::WAITING_BT);

    pinMode(WARNING_LED, OUTPUT); // Initialize external LED pin
}

void Robot::loop() {
    // Check for incoming Bluetooth messages (connection/disconnection notifications)
    _btManager.checkIncomingMessages();
    
    // These tasks run regardless of the current state
    checkSensors();
    updateMetrics();
    sendTelemetryIfNeeded();

    // Main state machine execution
    handleState();
}

void Robot::changeState(RobotState newState) {
    if (_currentState == newState) return;

    _currentState = newState;
    
    // Actions to take on entering a new state
    switch (_currentState) {
        case RobotState::WAITING_BT:
            _motors.stop();
            break;
        case RobotState::MANUAL:
            _btManager.sendTelemetry("event:manual_mode");
            _motors.stop();
            // Exit obstacle detection state when entering manual mode
            break;
        case RobotState::AUTO:
            _btManager.sendTelemetry("event:auto_mode");
            _motors.stop();
            break;
        case RobotState::OBSTACLE_DETECTED:
            _btManager.sendTelemetry("event:obstacle_detected");
            _motors.stop();
            break;
        case RobotState::STARTING:
             // Should not happen after setup
            break;
    }
}

void Robot::checkSensors() {
    if (millis() - _sensorCheckTimer > SENSOR_CHECK_INTERVAL) {
        _sensorCheckTimer = millis();

        _lastDistance = _usSensor.readDistance();
        _lastLightLevel = _photoresistor.readLightLevel();
        
        // Check for obstacles in AUTO mode only (not in MANUAL mode)
        if (_currentState == RobotState::AUTO) {
            if (_lastDistance >= 0 && _lastDistance < OBSTACLE_DISTANCE_THRESHOLD) {
                if (_currentState != RobotState::OBSTACLE_DETECTED) {
                    changeState(RobotState::OBSTACLE_DETECTED);
                }
            }
        }
        
        // Handle obstacle detection state
        if (_currentState == RobotState::OBSTACLE_DETECTED) {
            if (_lastDistance < 0 || _lastDistance >= OBSTACLE_DISTANCE_THRESHOLD) {
                // Obstacle cleared, clear LED and return to AUTO mode
                _ledMatrix.clear();
                changeState(RobotState::AUTO);
            }
        }
        
        // Check light level for headlights
        if (_lastLightLevel < LIGHT_THRESHOLD) {
            if (!_headlightsOn) {
                _headlightsOn = true;
                _ledMatrix.displayPattern(LEDMatrix::fullPattern); // Full brightness
                _btManager.sendTelemetry("event:headlights_on");
            }
        } else {
            if (_headlightsOn) {
                _headlightsOn = false;
                _ledMatrix.clear();
                _btManager.sendTelemetry("event:headlights_off");
            }
        }
    }
}

void Robot::handleState() {
    switch (_currentState) {
        case RobotState::WAITING_BT:
            handleWaitingBtState();
            break;
        case RobotState::MANUAL:
            handleManualState();
            break;
        case RobotState::AUTO:
            handleAutoState();
            break;
        case RobotState::OBSTACLE_DETECTED:
            handleObstacleDetectedState();
            break;
        default:
            // Should not happen
            break;
    }
}

void Robot::handleWaitingBtState() {
    // Check for manual mode request from IR remote
    unsigned long newCmd = _irRemote.readCommand();
    if (newCmd == IR_CMD_MANUAL_MODE) {
        changeState(RobotState::MANUAL);
        return;
    }
    
    // Check if Bluetooth is now connected
    if (_btManager.isConnected()) {
        _ledMatrix.clear();
        changeState(RobotState::AUTO);
        return;
    }
    
    // Display "Connect Bluetooth" message periodically on LED
    const unsigned long WAITING_DISPLAY_INTERVAL = 3000; // Display every 3 seconds
    if (millis() - _btWaitingDisplayTimer > WAITING_DISPLAY_INTERVAL) {
        _btWaitingDisplayTimer = millis();
        _ledMatrix.scrollTextBlocking("Connect Bluetooth", 50);
    }
}

void Robot::handleManualState() {
    unsigned long newCmd = _irRemote.readCommand();
    if (newCmd != 0) {
        // 0xFFFFFFFF is the IR repeat code - update the timestamp to keep the command active
        if (newCmd == 0xFFFFFFFF) {
            _lastIrTime = millis(); // Refresh the timeout timer on repeat signal
        } else {
            _lastIrCommand = newCmd;
            _lastIrTime = millis();
        }
    }

    if (millis() - _lastIrTime > IR_TIMEOUT) {
        _lastIrCommand = 0; // Clear command if no signal
    }
    
    if (_lastIrCommand == IR_CMD_AUTO_MODE) {
        // Check if Bluetooth is connected before switching to AUTO mode
        if (_btManager.isConnected()) {
            changeState(RobotState::AUTO);
        } else {
            // Not connected, go to WAITING_BT state instead
            changeState(RobotState::WAITING_BT);
        }
        return;
    }

    _motors.setSpeed(150); // Default speed for manual mode
    
    // Handle LED blinking for movement
    bool isMoving = false;

    switch (_lastIrCommand) {
        case IR_CMD_FORWARD: _motors.moveForward(); isMoving = true; break;
        case IR_CMD_BACKWARD: _motors.moveBackward(); isMoving = true; break;
        case IR_CMD_TURN_LEFT: _motors.rotateLeft(); isMoving = true; break;
        case IR_CMD_TURN_RIGHT: _motors.rotateRight(); isMoving = true; break;
        case IR_CMD_ROT_LEFT: _motors.rotateLeft(); isMoving = true; break;
        case IR_CMD_ROT_RIGHT: _motors.rotateRight(); isMoving = true; break;
        case IR_CMD_LIGHTS_ON:
            _ledMatrix.displayPattern(LEDMatrix::fullPattern);
            _btManager.sendTelemetry("event:lights_on");
            break;
        case IR_CMD_LIGHTS_OFF:
            _ledMatrix.clear();
            _btManager.sendTelemetry("event:lights_off");
            break;
        case IR_CMD_STOP: 
            _motors.stop(); 
            _btManager.sendTelemetry("event:emergency_stop");
            break;
        default: _motors.stop(); break;
    }
    
    // LED blink indicator when moving
    if (isMoving) {
        if (millis() - _ledBlinkTimer > LED_BLINK_INTERVAL) {
            _ledBlinkTimer = millis();
            // Toggle LED blink pattern
            static bool ledOn = true;
            if (ledOn) {
                analogWrite(WARNING_LED, HIGH); // Turn on external LED
            } else {
                analogWrite(WARNING_LED, LOW); // Turn off external LED
            }
            ledOn = !ledOn;
        }
    }
}

void Robot::handleAutoState() {
    // Check for switch to manual mode
    unsigned long newCmd = _irRemote.readCommand();
    if (newCmd == IR_CMD_MANUAL_MODE) {
        changeState(RobotState::MANUAL);
        return;
    }

    _motors.setSpeed(200); // Cautious speed for auto mode
    LineCorrection correction = _lineTracker.getCorrection();
    
    bool isMoving = false;

    switch(correction) {
        case LineCorrection::GO_STRAIGHT:
            _motors.moveForward();
            isMoving = true;
            break;
        case LineCorrection::TURN_LEFT:
            _motors.turnLeft();
            isMoving = true;
            break;
        case LineCorrection::TURN_RIGHT:
            _motors.turnRight();
            isMoving = true;
            break;
        case LineCorrection::GO_BACKWARD:
            _motors.moveBackward();
            isMoving = true;
            break;
        case LineCorrection::STOP:
            _motors.stop();
            break;
    }
    
    // LED blink indicator when moving
    if (isMoving) {
        if (millis() - _ledBlinkTimer > LED_BLINK_INTERVAL) {
            _ledBlinkTimer = millis();
            // Toggle LED blink pattern
            static bool ledOn = true;
            if (ledOn) {
                analogWrite(WARNING_LED, HIGH); // Turn on external LED
            } else {
                analogWrite(WARNING_LED, LOW); // Turn off external LED
            }
            ledOn = !ledOn;
        }
    }
}

void Robot::handleObstacleDetectedState() {
    // The robot is already stopped by changeState().
    // We wait here until the obstacle is cleared.
    // checkSensors() will trigger the state change back to AUTO.
    
    // Check if user wants to switch to manual mode despite obstacle
    unsigned long newCmd = _irRemote.readCommand();
    if (newCmd == IR_CMD_MANUAL_MODE) {
        changeState(RobotState::MANUAL);
        return;
    }

    // Light up the warning LED
    analogWrite(WARNING_LED, HIGH); // Turn on external LED
    
    // Display warning pattern continuously
    _ledMatrix.displayPattern(LEDMatrix::warningPattern);
}

void Robot::updateMetrics() {
    if(millis() - _cumulativeMetricsTimer > CUMULATIVE_METRICS_INTERVAL) {
        _cumulativeMetricsTimer = millis();
        _metricsManager.updateCumulative();
    }
    
    String modeStr = "UNKNOWN";
    switch(_currentState) {
        case RobotState::WAITING_BT: modeStr = "WAITING_BT"; break;
        case RobotState::MANUAL: modeStr = "MANUAL"; break;
        case RobotState::AUTO: modeStr = "AUTO"; break;
        case RobotState::OBSTACLE_DETECTED: modeStr = "OBSTACLE"; break;
        case RobotState::STARTING: modeStr = "STARTING"; break;
    }
    _metricsManager.update(modeStr, _lastDistance, _lastLightLevel, _lastIrCommand);
}

void Robot::sendTelemetryIfNeeded() {
    if (millis() - _telemetryTimer > TELEMETRY_INTERVAL) {
        _telemetryTimer = millis();
        String packet = _metricsManager.getTelemetryPacket();
        _btManager.sendTelemetry(packet);
    }
}
