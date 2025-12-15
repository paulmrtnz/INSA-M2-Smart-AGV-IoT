#include "MetricsManager.h"

// --- Physical Constants for Calculation ---
// NOTE: These values are placeholders and should be calibrated for the specific robot.
#define MAX_SPEED_CM_PER_S_AT_PWM_255 15.0

MetricsManager::MetricsManager(MotorController& motors) 
    : _motors(motors), _last_distance_calc_millis(0) {}

void MetricsManager::setup() {
    // Initialize all metrics to zero or default values
    _metrics.uptime_s = 0;
    _metrics.current_mode = "STARTING";
    _metrics.ultrasonic_distance_cm = 0.0;
    _metrics.last_ir_command = 0;
    _metrics.light_level = 0;
    _metrics.current_speed_pwm = 0;
    _metrics.distance_traveled_cm = 0.0;
    _last_distance_calc_millis = millis();
}

void MetricsManager::update(const String& mode, float distance, int lightLevel, unsigned long ir_command) {
    _metrics.uptime_s = millis() / 1000;
    _metrics.current_mode = mode;
    _metrics.ultrasonic_distance_cm = distance;
    _metrics.light_level = lightLevel;
    _metrics.current_speed_pwm = _motors.getCurrentSpeed();
    
    if (ir_command != 0) {
        _metrics.last_ir_command = ir_command;
    }
}

void MetricsManager::updateCumulative() {
    unsigned long current_millis = millis();
    float delta_t_s = (current_millis - _last_distance_calc_millis) / 1000.0;
    _last_distance_calc_millis = current_millis;

    int speed_pwm = _motors.getCurrentSpeed();
    float speed_cm_s = map(speed_pwm, 0, 255, 0, (int)(MAX_SPEED_CM_PER_S_AT_PWM_255 * 100)) / 100.0;

    float delta_distance = speed_cm_s * delta_t_s;
    _metrics.distance_traveled_cm += delta_distance;
}

const RobotMetrics& MetricsManager::getMetrics() const {
    return _metrics;
}

String MetricsManager::getTelemetryPacket() {
    String packet = "{";
    packet += "\"uptime_s\":" + String(_metrics.uptime_s) + ",";
    packet += "\"mode\":\"" + _metrics.current_mode + "\",";
    packet += "\"distance_cm\":" + String(_metrics.ultrasonic_distance_cm, 2) + ",";
    packet += "\"last_ir_cmd\":\"0x" + String(_metrics.last_ir_command, HEX) + "\",";
    packet += "\"light_level\":" + String(_metrics.light_level) + ",";
    packet += "\"speed_pwm\":" + String(_metrics.current_speed_pwm) + ",";
    packet += "\"dist_traveled_cm\":" + String(_metrics.distance_traveled_cm, 2);
    packet += "}";

    return packet;
}
