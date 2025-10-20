// Définition des types de trames Bluetooth
#pragma once

// Déclarations pour le buffer et le type de commande
#ifndef BLUETOOTH_SHARED_VARS
#define BLUETOOTH_SHARED_VARS

typedef enum BLECommand
{
  BLE_TYPE_NONE = 0x00,
  BLE_TYPE_CONSOLE = 0x01,
  BLE_TYPE_MATRIX = 0x02
} BLECommand;

extern unsigned char BLEBuffer[16];
extern BLECommand BLECommandType;

// Initialisation du module Bluetooth
void setup_BLE(void);

// Lire une trame de 16 octets via Bluetooth
bool BLE_read(void);

#endif