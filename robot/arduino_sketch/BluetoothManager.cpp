#include "BluetoothManager.h"

BluetoothManager::BluetoothManager() : _isConnected(false), _lastPingTime(0) {}

void BluetoothManager::setup(long baudRate) {
    // NOTE: This assumes the Bluetooth module is connected to the primary
    // hardware serial port (pins 0 and 1 on an Uno/Nano), which is also
    // used for USB communication and debugging.
    Serial.begin(baudRate);

    delay(1000); // Wait for the module to be ready

    // Configure the DX-BT24 module to send notifications on connection
    // AT+NOTI1 enables automatic notification when a connection is established
    // The module will send "OK+CONN" when connected
    Serial.write("AT+NOTI1\r\n");
    delay(500);
    
    // Drain any response from the module
    while (Serial.available()) {
        Serial.read();
    }
}

void BluetoothManager::sendTelemetry(const String& packet) {
    Serial.println(packet);
    _lastPingTime = millis(); // Update last communication time
}

void BluetoothManager::checkIncomingMessages() {
    // Poll for incoming messages from the Bluetooth module
    String incomingMessage = "";
    
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
            if (incomingMessage.length() > 0) {
                processIncomingMessage(incomingMessage);
                incomingMessage = "";
            }
        } else {
            incomingMessage += c;
        }
    }
}

void BluetoothManager::processIncomingMessage(const String& message) {
    // Check for connection notification - Once received, state persists until disconnection
    if (message.indexOf("OK+CONN") >= 0) {
        _isConnected = true;
        _lastPingTime = millis();
    }
    // Check for disconnection notification - Only way to change state back to disconnected
    else if (message.indexOf("OK+LOST") >= 0) {
        _isConnected = false;
    }
}

bool BluetoothManager::isConnected() {
    // Return the persistent connection status
    // State is updated via checkIncomingMessages() which is called from Robot::loop()
    return _isConnected;
}

