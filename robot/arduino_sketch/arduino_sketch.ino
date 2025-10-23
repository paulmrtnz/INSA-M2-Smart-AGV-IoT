#include "bluetooth.h"
#include "matrix.h"

unsigned char BLEBuffer[16];
BLECommand BLECommandType;

void setup() {
  setup_BLE();
  setup_led_matrix();
}

void loop() {
  // Lire les données Bluetooth
  if (BLE_read()) {
    switch (BLECommandType)
    {
    case BLE_TYPE_MATRIX:
      // Traiter la trame de type matrice
      matrix_display(BLEBuffer);
      break;
    case BLE_TYPE_CONSOLE:
      Serial.write(BLEBuffer, 16); // Affiche la réponse dans le moniteur série
      break;
    default:
      break;
    }
  }
}