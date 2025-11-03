
#define ML_PWM 6  // (EN) Left Motor Speed (PWM Pin)
#define ML_Ctrl 4    // (EN) Left Motor Direction (Digital Pin)
#define MR_PWM 5  // (EN) Right Motor Speed (PWM Pin)
#define MR_Ctrl 2    // (EN) Right Motor Direction (Digital Pin)


#define TURN_90_DELAY 2750 // to turn 90 degree i suppose it takes 600ms

int currentSpeed = 0;

void setup() {
  // Declaration 

  pinMode(ML_PWM, OUTPUT);
  pinMode(ML_Ctrl, OUTPUT);
  pinMode(MR_PWM, OUTPUT);
  pinMode(MR_Ctrl, OUTPUT);
  
  Serial.begin(9600); // Start to communicate with 9600m/s


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
  analogWrite(ML_PWM, 200);
  analogWrite(MR_PWM, 55);
}


void turnRight() {
  // we do inversely
  digitalWrite(ML_Ctrl, HIGH);
  digitalWrite(MR_Ctrl, LOW);
  analogWrite(ML_PWM, 55);
  analogWrite(MR_PWM, 200);
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
  setSpeed(155);//  Speed (m/s) = (pi * D × Motor RPM) / 60
  // 150 RPM 

  moveForward();// go forward
  delay(1000); // wait for 1s

  moveBackward();// go backward
  delay(1000);// wait for 1s
  stopRobot();// stop the robot and wait for 2s

  turnLeft();// turn left
  delay(1000);// wait for 0.5s
  stopRobot();

  turnRight();// turn right 
  delay(1000);// wait for 0.5s
  stopRobot();


  turnLeft();
  delay(500);
  moveForward();
  delay(1000);

  turnRight();
  delay(500);
  moveBackward();
  delay(1000);



  unsigned long start= millis()
  turnDegrees(90);// turn 90 degree on the right
  unsigned long t = millis() - start
  Serial.print(t)
  Serial.println("ms")


  // turnDegrees(-90);// turn to the initial position 
  // stopRobot();
}