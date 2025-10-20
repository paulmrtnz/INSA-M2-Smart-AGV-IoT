#include "bluetooth.h"
#include "matrix.h"

void setup_BLE() {
  Serial.begin(9600);  // Serial = RX0/TX1 = module BT24

  delay(1000); // Attendre que le module soit prêt

  // Envoyer la commande AT pour obtenir l'adresse MAC
  Serial.print("AT+LADDR\r\n");

  delay(300); // Attendre la réponse du module

  // Lire et afficher la réponse reçue
  while (Serial.available()) {
    char c = Serial.read();
    Serial.write(c); // Affiche la réponse dans le moniteur série
  }
}

// Fonction pour lire une trame de 16 octets via Bluetooth
bool BLE_read() {
  static int byteIndex = 0;  // Position actuelle dans le buffer
  static bool waitingForCommand = true;
  while (Serial.available() > 0) {
    unsigned char receivedByte = Serial.read();
    if (waitingForCommand) {
      // Premier octet = type de commande
      BLECommandType = (BLECommand)receivedByte;
      byteIndex = 0;
      waitingForCommand = false;
    } else {
      // Stocker l'octet reçu dans le buffer
      BLEBuffer[byteIndex] = receivedByte;
      byteIndex++;
      // Si on a reçu 16 octets (trame complète)
      if (byteIndex >= 16) {
        waitingForCommand = true;
        byteIndex = 0;
        return true; // Trame complète prête
      }
    }
  }
  return false;  // Pas encore de trame complète
}