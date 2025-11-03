
#define ML_PWM 6  // (EN) Left Motor Speed (PWM Pin)
#define ML_Ctrl 4    // (EN) Left Motor Direction (Digital Pin)
#define MR_PWM 5  // (EN) Right Motor Speed (PWM Pin)
#define MR_Ctrl 2    // (EN) Right Motor Direction (Digital Pin)


#define TURN_90_DELAY 600 // to turn 90 degree i suppose it takes 600ms

int currentSpeed = 0;

void setup() {
  // Declaration 

  pinMode(ML_PWM, OUTPUT);
  pinMode(ML_Ctrl, OUTPUT);
  pinMode(MR_PWM, OUTPUT);
  pinMode(MR_Ctrl, OUTPUT);


  digitalWrite(ML_PWM, LOW);
  digitalWrite(MR_PWM, LOW);
}


void setSpeed(int speed) {

  if (speed < 0) speed = 0;
  if (speed > 255) speed = 255;
  currentSpeed = speed;
}


void moveForward() {
  digitalWrite(ML_Ctrl, HIGH);
  digitalWrite(MR_Ctrl, HIGH);
  analogWrite(ML_PWM, currentSpeed);
  analogWrite(MR_PWM, currentSpeed);
}


void moveBackward() {
  digitalWrite(ML_Ctrl, LOW);
  digitalWrite(MR_Ctrl, LOW);
  analogWrite(ML_PWM, currentSpeed);
  analogWrite(MR_PWM, currentSpeed);
}


void turnLeft() {
  //  Left wheel backward, Right wheel forward

  digitalWrite(ML_Ctrl, LOW);
  digitalWrite(MR_Ctrl, HIGH);
  analogWrite(ML_PWM, currentSpeed);
  analogWrite(MR_PWM, currentSpeed);
}


void turnRight() {
  // we do inversely
  digitalWrite(ML_Ctrl, HIGH);
  digitalWrite(MR_Ctrl, LOW);
  analogWrite(ML_PWM, currentSpeed);
  analogWrite(MR_PWM, currentSpeed);
}


void stopRobot() {

  digitalWrite(ML_Ctrl,LOW); // set the dir of moteur left is low
  digitalWrite(MR_Ctrl,LOW);
  analogWrite(ML_PWM, 0);// speed moteurs right is 0  
  analogWrite(MR_PWM, 0);// speed moteurs left is 0 
  delay(2000);// stop in 2s
}


void turnDegrees(int degrees) {

  long turnDelay = map(abs(degrees), 0, 90, 0, TURN_90_DELAY);// transform degree into the duration  
  // map(value, fromLow, fromHigh, toLow, toHigh)

  if (degrees > 0) {
    turnRight();
  } else {
    turnLeft();
  }


  delay(turnDelay);// 


  stopRobot();
}


void loop()
{
  setSpeed(155);//  Speed (m/m) = (Wheel circumference × Motor RPM) / 60

  moveForward();// go forward
  delay(1000); // wait for 1s
  moveBackward();// go backward
  delay(1000);// wait for 1s
  stopRobot();// stop the robot and wait for 2s

  turnLeft();// turn left
  delay(500);// wait for 0.5s

  turnRight();// turn right 
  delay(500);// 
  turnDegrees(30);// turn 30 degree on the left
  delay(1000); // wait for 1 s
  turnDegrees(-30);// turn to the initial position 
  delay(1000);// wait for 1 s
}