#include "motors.h"

void setup_motors(void) {
    pinMode(ML_Ctrl, OUTPUT); 
    pinMode(ML_PWM, OUTPUT); 
    pinMode(MR_Ctrl, OUTPUT); 
    pinMode(MR_PWM, OUTPUT); 
}

void move_forward(void) {
    digitalWrite(ML_Ctrl, HIGH); 
    analogWrite(ML_PWM, 55); 
    digitalWrite(MR_Ctrl, HIGH); 
    analogWrite(MR_PWM, 55); 
}

void move_backward(void) {
    digitalWrite(ML_Ctrl, LOW); 
    analogWrite(ML_PWM, 200); 
    digitalWrite(MR_Ctrl, LOW); 
    analogWrite(MR_PWM, 200); 
}

void turn_left(void) {
    digitalWrite(ML_Ctrl, LOW); 
    analogWrite(ML_PWM, 200);   
    digitalWrite(MR_Ctrl, HIGH);
    analogWrite(MR_PWM, 55);    
}

void turn_right(void) {
    digitalWrite(ML_Ctrl, HIGH);
    analogWrite(ML_PWM, 55);
    digitalWrite(MR_Ctrl, LOW);
    analogWrite(MR_PWM, 200);
}

void stop_motors(void) {
    digitalWrite(ML_Ctrl, LOW);
    analogWrite(ML_PWM, 0);
    digitalWrite(MR_Ctrl, LOW);
    analogWrite(MR_PWM, 0); 
}