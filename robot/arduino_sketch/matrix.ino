
#include <Arduino.h>
#include "matrix.h"
#include "bluetooth.h"

unsigned char smile[16] = { 0x00, 0x00, 0x10, 0x20, 0x40, 0x40, 0x4c, 0x40, 0x40, 0x4c, 0x40, 0x40, 0x20, 0x10, 0x00, 0x00 };

void setup_led_matrix() {
  //set the pin to OUTPUT
  pinMode(SCL_Pin, OUTPUT);
  pinMode(SDA_Pin, OUTPUT);

  matrix_clear();

  // Initialiser le buffer avec le smile par défaut
  memcpy(BLEBuffer, smile, 16);

  // Afficher le smile au démarrage
  matrix_display(BLEBuffer);
}

void matrix_display(unsigned char matrix_value[]) {
  IIC_start();
  IIC_send(0xc0);

  for (int i = 0; i < 16; i++) {
    IIC_send(matrix_value[i]);
  }

  IIC_end();

  IIC_start();
  IIC_send(0x8A);
  IIC_end();

  BLECommandType = BLE_TYPE_NONE;  // Réinitialiser le type de commande après affichage
}

void matrix_clear() {
  unsigned char clear_data[16] = {0};
  matrix_display(clear_data);
}

void IIC_start() {
  digitalWrite(SDA_Pin, HIGH);
  digitalWrite(SCL_Pin, HIGH);
  delayMicroseconds(3);
  digitalWrite(SDA_Pin, LOW);
  delayMicroseconds(3);
  digitalWrite(SCL_Pin, LOW);
}


void IIC_end() {
  digitalWrite(SCL_Pin, LOW);
  digitalWrite(SDA_Pin, LOW);
  delayMicroseconds(3);
  digitalWrite(SCL_Pin, HIGH);
  delayMicroseconds(3);
  digitalWrite(SDA_Pin, HIGH);
  delayMicroseconds(3);
}


void IIC_send(unsigned char send_data) {
  for (byte mask = 0x01; mask != 0; mask <<= 1)  //each character has 8 digits, which is detected one by one
  {
    if (send_data & mask) {  //set high or low levels in light of each bit(0 or 1)
      digitalWrite(SDA_Pin, HIGH);
    } else {
      digitalWrite(SDA_Pin, LOW);
    }
    delayMicroseconds(3);
    digitalWrite(SCL_Pin, HIGH);  //pull up the clock pin SCL_Pin to end the transmission of data
    delayMicroseconds(3);
    digitalWrite(SCL_Pin, LOW);  //pull down the clock pin SCL_Pin to change signals of SDA
  }
}