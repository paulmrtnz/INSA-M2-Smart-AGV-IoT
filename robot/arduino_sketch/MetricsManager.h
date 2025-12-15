#ifndef METRICS_MANAGER_H
#define METRICS_MANAGER_H

#include <Arduino.h>
#include "MotorController.h"

// Data structure to hold all robot metrics
struct RobotMetrics {
    unsigned long uptime_s;
    String current_mode;
    float ultrasonic_distance_cm;
    unsigned long last_ir_command;
    int light_level;
    int current_speed_pwm;
    float distance_traveled_cm;
};

class MetricsManager {
public:
    explicit MetricsManager(MotorController& motors);
    void setup();

    // Updates instantaneous metrics
    void update(const String& mode, float distance, int lightLevel, unsigned long ir_command);

    // Updates cumulative metrics like distance. Should be called periodically.
    void updateCumulative();

    // Builds the telemetry data packet (JSON format)
    String getTelemetryPacket();

    // Allows direct access to the metrics data if needed
    const RobotMetrics& getMetrics() const;

private:
    MotorController& _motors;
    RobotMetrics _metrics;
    unsigned long _last_distance_calc_millis;
};

#endif // METRICS_MANAGER_H
