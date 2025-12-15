#ifndef BLUETOOTH_MANAGER_H
#define BLUETOOTH_MANAGER_H

#include <Arduino.h>

class BluetoothManager {
public:
    BluetoothManager();
    void setup(long baudRate = 9600);
    void sendTelemetry(const String& packet);
    bool isConnected();
    void checkIncomingMessages(); // Poll for incoming BT connection messages

private:
    // This class assumes the Bluetooth module is on the main `Serial` port.
    bool _isConnected;
    unsigned long _lastPingTime;
    
    void processIncomingMessage(const String& message);
};

#endif // BLUETOOTH_MANAGER_H
