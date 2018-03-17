//  v1:
//  -serial communication to arduino
//  -toDO: implement cases b - g
//
//  v2:
//  servos are controlled directly in loop
//  fixed motors comtroller
//  serial communication to arduino convention:
//
//  v2_4:
//  servos work independently
//  missing code for Positioner and Claw
//  a-100
//  Letter[specific engine] + number(positive or negative)[power or position for specific motor]
//  one command at the time
//  test range for Rotor
//  v2_4_1:
//  better names

// v3:
// merged Pawel's and Demo i2c program
// replacing serial communication by i2c and implementation


//  Letters - motors/servos library;

//  a   - (right)      - driving motor right (positive - forward)
//  b   - (Left)       - driving motor left (positive - forward)
//  c   - (Positioner) - motor rotating whole arm
//  d/0 - (Bot)        - servo down for arm (position 180 is arm closed) (move 0 - 180)
//  e/1 - (Mid)        - servo mid for arm (position 180 is arm closed) (move 0 - 180)
//  f/2 - (Mid)        - servo changing position of hand
//  g   - (Claw)       - motor closing hand (0 - open, 1 - close) (constant speed)
//  h/3 - (Rotor)      - servo rotating hand

//////////////////////

//list of people interested
//on229, kcj21, pg476

#include <Servo.h>


//MOVING MOTORS ////////////////////////
#define MOTOR_R_DIR 12
#define MOTOR_R_ADIR 13
#define MOTOR_R_PWM 8

#define MOTOR_L_DIR 10
#define MOTOR_L_ADIR 11
#define MOTOR_L_PWM 9

//CLAW MOTORS
#define ClawA 28 
#define ClawB 30
#define ClawPWM 2


//Stand by pin for the tb6621fng motor driver. This must be HIGH to use the claw and roter.
#define STBY 22

//SERVOS////////////////////////////////
#define servo_Bot_num 7
#define servo_Mid_num 6
#define servo_Swinger_num 5
#define servo_Rotor_num 4

Servo servos[4];
int servos_pos[4];  //Bot Mid Swinger  Rotor
int servos_goto_pos[4] = {175, 180, 93, 180};
int pos_goto_temp;

//SERIAL COMMUNICATION VARIABLES ////////////////////////
char incoming_type = '*';
int incoming_value;
boolean new_command;


//TIME VARIABLES
unsigned long timeReadServosPositionsStart, timeReadServosPositionsEnd;
unsigned long timeLoopStart, timeLoopEnd;
unsigned long timeSerialStart, timeSerialEnd;
unsigned long this_time_servos, last_time_servos;

//Communication
#include <Wire.h>


int message = 0;
int store[2000];
int store_vals = 0;

int SLAVE_ADDRESS = 0x04;   //i2c address for this arduino = 0x04

//----------SETUP--------------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  Serial.println("HI, starting the program");
  Serial.setTimeout(5);//try boosting :) - this works for 9600 communication speed

  //Driving motors
  pinMode(MOTOR_R_DIR, OUTPUT);
  pinMode(MOTOR_R_ADIR, OUTPUT);
  pinMode(MOTOR_R_PWM, OUTPUT);
  pinMode(MOTOR_L_DIR, OUTPUT);
  pinMode(MOTOR_L_ADIR, OUTPUT);
  pinMode(MOTOR_L_PWM, OUTPUT);

  //Claw motors
  pinMode(ClawA, OUTPUT);
  pinMode(ClawB, OUTPUT);
  pinMode(ClawPWM, OUTPUT);

  // STBY
  pinMode(STBY, OUTPUT);

  //Servos
  
  servos[0].attach(servo_Bot_num);
  servos[1].attach(servo_Mid_num);
  servos[2].attach(servo_Swinger_num);
  servos[3].attach(servo_Rotor_num);

  //delay(2000); //time for servos
  last_time_servos = millis();//Time for servos speed

  //Communication
  //Begin i2c communication
  Wire.begin(SLAVE_ADDRESS);

  // whenever the device recieves a signal this program is called
  Wire.onReceive(ReceiveMassage); 
  
  // when ever this device is asked for a signal it runs this code
  Wire.onRequest(RequestMassage);
}

//----------LOOP--------------------------------------------------------------------------------
void loop() {

    delay(15);
    //timeLoopStart = millis();
    read_servos_positions();
    //Activate servos
    servos_thread();
  
}

///////////////////////////////////////////////////////////////////
/////////////////////FUNCTIONS/////////////////////////////////////
///////////////////////////////////////////////////////////////////

void executeOrder(){
  Serial.print("Executing order: ");
  Serial.print(incoming_type);
  Serial.println(incoming_value);
  switch (incoming_type) {
      case 'a':  //(Right)
        //Serial.println("you chose a");
        drive_controller(1, incoming_value);
        break;

      case 'b':  //(Left)
        drive_controller(0, incoming_value);
        break;

      case 'c':  //(Positioner)
        //arm_motors_controller(); - to be written - for rotating arm and closing hand (c, g)
        break;

      case 'd':  //(Bot)
        servos_goto_pos[0] = incoming_value;
        break;

      case 'e':  //(Mid)
        servos_goto_pos[1] = incoming_value;
        break;

      case 'f':  //(Swinger)
        servos_goto_pos[2] = incoming_value;
        break;

      case 'g':  //(Claw) Works but the delay() function is not behaving as it should be
        Serial.println("claw mode activated");
        claw(incoming_value);
        Serial.print("incoming value"); Serial.println(incoming_value);
        break;
        
      case 'h':  //(Rotor)
        servos_goto_pos[3] = incoming_value;
        break;

      default:
        Serial.println("Incorrect input");
    }
    incoming_type = '*';
}

///////////////////SERIAL READER///////////////////////////////////////////////////////////////////////////////////////////////////////////

void ReceiveMassage(int n){
  int value = Wire.read();
  Serial.println(value);
  if(incoming_type == '*'){
    incoming_type = char(value);
  }else{
    if(value > 128){
      value = -256 + value;
    }
    if(incoming_type == "a" || incoming_type == "b"){
      value = value *2;
    }
    incoming_value = value;
    executeOrder();
  }
}

void RequestMassage(){
  Wire.write(72);//ord of H
  message = 'T';
}

///////////////////MOTORS FOR WHEELS////////////////////////////////////////////////////////////////////////////////////////////////////////
void drive_controller(boolean motor, int motor_speed) {  //1 - right, o - left
  boolean dir = 1;
  if (motor_speed < 0) {
    dir = 0;
    motor_speed = -motor_speed;
  }
  if (motor) {
    digitalWrite(MOTOR_R_DIR, (dir ? HIGH : LOW));
    digitalWrite(MOTOR_R_ADIR, (dir ? LOW : HIGH));
    analogWrite(MOTOR_R_PWM, motor_speed);
  }
  else {
    digitalWrite(MOTOR_L_DIR, (dir ? HIGH : LOW));
    digitalWrite(MOTOR_L_ADIR, (dir ? LOW : HIGH));
    analogWrite(MOTOR_L_PWM, motor_speed);
  }
}

///////////////////CLAW PROGRAM////////////////////////////////////////////////////////////////////////////////////////////////////////
void claw(boolean dir) {  

  digitalWrite(STBY, HIGH); 
 
  digitalWrite(ClawA, (dir ? LOW : HIGH));
  digitalWrite(ClawB, (dir ? HIGH : LOW));
  analogWrite(ClawPWM,255);

  // not sure why delay function is not working as it is supposed to. 
  // 10000 roughly corresponds to 100ms. 
  delay(20000);
  
  digitalWrite(ClawA, LOW); digitalWrite(ClawB, LOW);
  digitalWrite(STBY, LOW);
}



///////////////////READ POSITIONS AND SEND INFO ABOUT SERVOS ARM///////////////////////////////////////////////////////////////////////////////////////////////////////////
void read_servos_positions() {
  servos_pos[0] = servos[0].read();
  servos_pos[1] = servos[1].read();
  servos_pos[2] = servos[2].read();
  servos_pos[3] = servos[3].read();

  /*
  Serial.println("Bot Mid Swinger Rotor");
  Serial.print(servos_pos[0]);
  Serial.print("  ");
  Serial.print(servos_pos[1]);
  Serial.print("  ");
  Serial.print(servos_pos[2]);
  Serial.print("  ");
  Serial.println(servos_pos[3]);

  Serial.print(servos_goto_pos[0]);
  Serial.print("  ");
  Serial.print(servos_goto_pos[1]);
  Serial.print("  ");
  Serial.print(servos_goto_pos[2]);
  Serial.print("  ");
  Serial.println(servos_goto_pos[3]);

  */
}


void servos_thread() {
  this_time_servos = millis();


  for (int i = 0; i < 4; i ++) {
    if (servos_goto_pos[i] != servos_pos[i]) {

      if (servos_goto_pos[i] > servos_pos[i]) {
        pos_goto_temp = servos_pos[i] + (this_time_servos - last_time_servos) / 5;
        if (pos_goto_temp > servos_goto_pos[i]) {
          pos_goto_temp = servos_goto_pos[i];
        }
      }

      if (servos_goto_pos[i] < servos_pos[i]) {
        pos_goto_temp = servos_pos[i] - (this_time_servos - last_time_servos) / 5;
        if (pos_goto_temp < servos_goto_pos[i]) {
          pos_goto_temp = servos_goto_pos[i];
        }
      }

      servos[i].write(pos_goto_temp);
    }
  }
  last_time_servos = millis();
}




