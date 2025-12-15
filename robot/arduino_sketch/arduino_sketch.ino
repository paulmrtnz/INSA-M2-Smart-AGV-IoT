#include "Robot.h"

// Create the single, global instance of our Robot
Robot robot;

void setup() {
  // Initialize the robot and all its components
  robot.setup();
}

void loop() {
  // Run the robot's main loop
  robot.loop();
}