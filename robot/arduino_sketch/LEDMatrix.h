#ifndef LED_MATRIX_H
#define LED_MATRIX_H

#include <Arduino.h>

class LEDMatrix {
public:
    LEDMatrix(int sclPin, int sdaPin);
    void setup();

    // Display a static 16-byte pattern
    void displayPattern(const byte pattern[16]);

    // Clear the display
    void clear();

    // --- Text Scrolling ---
    // A blocking function, only suitable for setup()
    void scrollTextBlocking(const String& text, int scrollSpeed = 100);

    // --- Public Patterns ---
    static const byte smilePattern[16];
    static const byte PGPLogo[16];
    static const byte fullPattern[16];
    static const byte warningPattern[16];

private:
    void IIC_start();
    void IIC_end();
    void IIC_send(byte send_data);
    int getFontIndex(char c);

    int _sclPin;
    int _sdaPin;

    // Font data
    static const byte font5x8[][5];
};

#endif // LED_MATRIX_H
