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

// v4: 
// included claw program
// included interface program for arm manipulation

// v5: (v1 of this file)
// made arm manipulation possible

// v6: 
// modified the servo control part of the file 

// v7: 
// Changed the servo pins due to chassis redesign, altered claw function

// v8:
// Added funciton for the base rotor of the arm and using the gyroscope


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

// standard servo libraray 
#include <Servo.h>


//MOVING MOTORS ////////////////////////
#define MOTOR_R_DIR 36
#define MOTOR_R_ADIR 38
#define MOTOR_R_PWM 11

#define MOTOR_L_DIR 32
#define MOTOR_L_ADIR 34
#define MOTOR_L_PWM 10

//CLAW MOTORS
#define ClawA 15 
#define ClawB 14
#define ClawPWM 46

//BASE MOTORS
#define BaseA 17 
#define BaseB 16
#define BasePWM 7


//Stand by pin for the tb6621fng motor driver. This must be HIGH to use the claw and roter.
#define STBY 28

//magnetic encoder pin
#define magpin 26

//SERVOS////////////////////////////////
#define servo_Bot_num 2
#define servo_Mid_num 3
#define servo_Swinger_num 4
#define servo_Rotor_num 6
#define servo_Roll_num 5

Servo servos[5];
int servos_pos[4];  //Bot Mid Swinger  Rotor
int servos_goto_pos[4] = {180, 180, 93, 180};
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


//MPU6050 stuff. For gyroscope
#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;
float integral = 0;


int message = 0;
int store[2000];
int store_vals = 0;

int SLAVE_ADDRESS = 0x04;   //i2c address for this arduino = 0x04


//Variables used:
int alpha = 0; //base servo angle
int beta = 0; //mid servo angle
bool is_alpha_in = true; //notify the code when two values have come through

bool order = false; // this boolean will determine whether to call the executeOrder function
                    // this is here because within the interrupt funciton, delays are useless

int curralpha = 0;
int currbeta = 0;


//variables for base rotor position
int curr_pos = 0;
int prev_state = 0;
bool base_dir = true; // left = true, right = false


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

  //Base motors
  pinMode(BaseA, OUTPUT);
  pinMode(BaseB, OUTPUT);
  pinMode(BasePWM, OUTPUT);

  // STBY
  pinMode(STBY, OUTPUT);

  // magpin
  pinMode(magpin, INPUT);

  
  //Servos
  servos[0].attach(servo_Bot_num);
  servos[1].attach(servo_Mid_num);
  servos[2].attach(servo_Swinger_num);
  servos[3].attach(servo_Rotor_num);
  servos[4].attach(servo_Roll_num);

  //MPU6050 Commands
  // check if MPU6050 is present
  while(!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G))
  {
    Serial.println("Could not find a valid MPU6050 sensor, check wiring!");
    delay(500);
  }
  // calibration
  mpu.calibrateGyro();
  mpu.setThreshold(3);


  //delay(2000); //time for servos
  //last_time_servos = millis();//Time for servos speed

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
  digitalWrite(STBY, HIGH);
  Serial.println(curr_pos);

  base_dir = false;
  digitalWrite(BaseA, LOW); digitalWrite(BaseB, HIGH);
      analogWrite(BasePWM, 200);
  long t = millis(); 
  while(millis() - t < 600) {
    count_pos();
  }
  
  Serial.println(curr_pos);
  digitalWrite(BaseA, LOW); digitalWrite(BaseB, LOW);

  delay(500);

  datum();
  
  delay(99999999999);
    
    /*digitalWrite(STBY, HIGH);
    
    digitalWrite(ClawA, HIGH);
    digitalWrite(ClawB, LOW);
    digitalWrite(ClawPWM, HIGH);
    delay(200);
    
    digitalWrite(ClawA, LOW);
    digitalWrite(ClawB, LOW);

    delay(999999999);
  */
    digitalWrite(STBY, HIGH);
    
    servos[0].write(180);
    servos[1].write(178);
    servos[2].write(82);
    servos[3].write(80);
    servos[4].write(80);
    delay(2000);

    while(true) {
      if(base_moving = true) {
        count_pos();
      }
      
      if(order == true) {
        order = false;
        executeOrder();
      }
    }
    /*
    delay(15);
    //timeLoopStart = millis();
    read_servos_positions();
    //Activate servos
    servos_thread();
    */
  
}

///////////////////////////////////////////////////////////////////
/////////////////////FUNCTIONS/////////////////////////////////////
///////////////////////////////////////////////////////////////////

void executeOrder(){
  
  Serial.print("Executing order: ");
  if(incoming_type != 'i') {
    Serial.print(incoming_type);
    Serial.println(incoming_value);
  }
  else {
    Serial.println("Arm is called"); 
    Serial.print(incoming_type); 
    Serial.print(" A="); Serial.print(alpha);
    Serial.print(" B="); Serial.println(beta);
  }
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
        servos[2].write(incoming_value);
        //servos_goto_pos[1] = incoming_value;
        break;

      case 'f':  //(Swinger)
        servos[3].write(incoming_value);
        //servos_goto_pos[2] = incoming_value;
        break;

      case 'g':  //(Claw) Works but the delay() function is not behaving as it should be
        Serial.println("claw mode activated");
        Serial.println(incoming_value);
        incoming_type = '*';
        claw(incoming_value);
        break;
        
      case 'h':  //(Rotor)
        servos[4].write(incoming_value);
        //servos_goto_pos[3] = incoming_value;
        break;

      case 'i': // arm xy test
        Serial.println("Arm will be activated");
        incoming_type = '*';
        movearm();
        break;

      case 'j': // base rotor movement
        Serial.println("base rotor movement activated");
        incoming_type = '*';
        base(incoming_value);
        break;

      case 'k': // functions using motion control by the gyro called here
        Serial.println("Gyro control programs called here");
        incoming_type = '*';
        // call function here
        break;
        
      default:
        Serial.println("Incorrect input");
    }
    if(order == false){
      incoming_type = '*';
    }
}

///////////////////SERIAL READER///////////////////////////////////////////////////////////////////////////////////////////////////////////

void ReceiveMassage(int n){
  int value = Wire.read();
  Serial.print("Reading value in: "); Serial.println(value);

  //if incoming type is not set, ie: a new message is recieved 
  if(incoming_type == '*'){
    incoming_type = char(value);

    // if incoming type is about the arm
    if(incoming_type == 'i') {
      is_alpha_in = false;
    }
  }
  else{
    //Serial.println(incoming_type);

    // if we are looking at incoming value for the arm angles
    if(incoming_type == 'i') {
      if(is_alpha_in == false){
        // none of the angles have come in, thus, this value is alpha (first angle)
        alpha = value;
        is_alpha_in = true;
      }
      else {
        // is_alpha_in = true i.e. alpha is set, this value is b
        beta = value;
        
        //order will be executed in the main loop
        order = true;  
      }
    }
    // if incoming command is for the claw, base, or move straight
    else if(incoming_type == 'g' || incoming_type == 'j' || incoming_type == 'k') {
      incoming_value = value;
     
      //order will be executed in the main loop
      order = true;
    }
    else {
      if(incoming_type == 'd' ||incoming_type == 'e' ||
      incoming_type == 'f' || incoming_type == 'h' ){
        Serial.println("GOT IT");
      }
      else {
        if(value > 128){
          value = -256 + value;
        }
        if(incoming_type == 'a' || incoming_type == 'b'){
          value = value *2;
        }
      }
      incoming_value = value;
       Serial.print("value processed"); Serial.println(value);
       //order = true;
      executeOrder();
    }
    
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
  Serial.println("here");
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

// function to move claw
void claw(boolean dir) {  
 
  digitalWrite(ClawA, (dir ? LOW : HIGH));
  digitalWrite(ClawB, (dir ? HIGH : LOW));
  analogWrite(ClawPWM,255);

  long t1 = millis();
  while(millis() - t1 < 200) {
    //break this loop and go back to main loop, if an order comes through while the claw is in action
    if(order == true) {
      break;
    }
  }
  
  digitalWrite(ClawA, LOW); digitalWrite(ClawB, LOW);
}

///////////////////BASE PROGRAM////////////////////////////////////////////////////////////////////////////////////////////////////////

// function to count relative position as the magnetic sensor changes 
void count_pos() {
  int val = digitalRead(magpin);
  if(val != prev_state) {
    if(base_dir == true) {curr_pos += 1;}
    else {curr_pos -= 1;}

    prev_state = val;
  }
}

// function to bring the arm back to the datum position based on curr_pos
void datum() {
  curr_pos = int(curr_pos*0.9); // fudge factor for position
  if(curr_pos <= 0) {
    base_dir = true; // currently have turned right. so will turn left towards datum
    digitalWrite(BaseA, HIGH); digitalWrite(BaseB, LOW);
    analogWrite(BasePWM, 200);
    while(curr_pos <= 0) {
      count_pos();
    }
  }
  else {
    base_dir = false; // currently have turned left. so will turn right towards datum
    digitalWrite(BaseA, LOW); digitalWrite(BaseB, HIGH);
    analogWrite(BasePWM, 200);
    while(curr_pos > 0) {
      count_pos();
    }
  }
  digitalWrite(BaseA, LOW); digitalWrite(BaseB, LOW);
  Serial.println(curr_pos);
}


// function to move base through incmoing command from RPi
void base(int command) {

  Serial.println(command); 
  switch(command) {

    
    case 1:
      base_dir = true;
      digitalWrite(BaseA, HIGH); digitalWrite(BaseB, LOW);
      analogWrite(BasePWM, 200);
      break;
    case 2: 
      base_dir = false;
      digitalWrite(BaseA, LOW); digitalWrite(BaseB, HIGH);
      analogWrite(BasePWM, 200);
      break;
    case 0:
      digitalWrite(BaseA, LOW); digitalWrite(BaseB, LOW);
      break;
    default:
      digitalWrite(BaseA, LOW); digitalWrite(BaseB, LOW);
      break;
  }
    

}

///////////////////READ GYROSCOPE///////////////////////////////////////////////////////////////////////////////////////////////////////////
// call when calibrating the sensor 
void gyro_calib() {
  // calibration
  mpu.calibrateGyro();
  mpu.setThreshold(3);
  integral = 0;
}


float MoveStraight() {
  // this part of the program must be made

  
}

/* More programs using the gyroscope can and probably should be made. 
 *  Ideas include such as but not limited to: turning 90 degrees shifting horisonal position by x(cm), Seeing how the "push" mechanism changed the relative angle of the robot
 */

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

// Pawel's program on servo control
void servos_thread() {
  //this_time_servos = millis();


  for (int i = 0; i < 4; i ++) {
    if (servos_goto_pos[i] > servos_pos[i] + 4 || servos_goto_pos[i] < servos_pos[i] - 2 ) {

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
  //last_time_servos = millis();
}

////////// TWO SERVO CONTROL PROGRAM FOR ARM MANIPULATION ///////////////////////////////////////////////////////////////////////////////////////////////////

  // alpha = angle of first servo     beta = angle of second servo
  // first servo is the one on the base of the arm

  // change definition of alpha and beta because the servos are inverted in position. 
  // i.e.: arm flat on the ground = 180 degrees not 0 degrees
  alpha = 194-alpha;
  beta = 178-beta;

  // boundary conditions for servos
  if(alpha > 180) {alpha = 180;}
  if(alpha < 0) {alpha = 0;}
  if(beta > 178) {beta = 178;}
  if(beta < 0) {beta = 0;}

  Serial.println("will activate moveservo");
  moveservo(alpha,beta);

}

// moving the arm program Inverse kinematics
/* The idea of this funciton is to take the difference between 
 * the current angle of the servo and the target angle (alpha, beta)
 * and then move each servo to that target angle.
 * 
 * However, since moving the servo normally would result in a abrupt 
 * movement of the arm, to smooth it, delays are inserted between 
 * each angle each servo makes. 
 * 
 * To make the movement even more smoother, the program will change the 
 * amount of delay between angles depending of the relative position 
 * of the servo, so that the the servo rotates slowly at the beggining 
 * and the end of the rotation process, while moving fast in between.
 * 
 * To achieve this, the amount of delay at each degree interval is a quadratic
 * function of the relative position. 
  */
void moveservo(int n, int m) {

  // n = the angle fed into the first servo i.e.: alpha. 
  // m = the angle fed into the sercond servo i.e.: beta.
    
  Serial.print("values into the function: ");
  Serial.print(n); Serial.print(", "); Serial.println(m);

  // gpos = angle fed into the third servo (the tip angle of the gripper)
  // this formula becomes a bit dodgy when it goes to extreme angles. This is because at extremes, theoretical angles ≠ real angles
  int gpos = 82+n-m;

  // calcualte difference in angle (degrees) of each servo
  int currval1=servos[0].read();
  int count1 = abs(currval1-n);

  int currval2=servos[1].read();
  int count2 = abs(currval2-m);

  int currval3=servos[2].read();
  int count3 = abs(currval3-gpos);

  // set parameteres of the quadratic function. 
  // t_min is the minimum delay time, which happens at the angle = n/2, if total movement = n degrees
  // t_0 is the maximum delay time, which will happen at angle = 0 and angle = n
  int tmin_a = 20;
  int t0_a = 40;
  int t_a; int x_a = 0;

  int tmin_b = 20;
  int t0_b = 40;
  int t_b; int x_b = 0;

  int tmin_c = 20;
  int t0_c = 30;
  int t_c; int x_c = 0;

  // reset three timers involved in moving each servo
  long a = millis();
  long b = millis();
  long c = millis();
  
  while(true) {
    // Calculate the delay time for each servo. 
    
    //calculate time FOR A
    t_a = (4/(pow(count1,2)))*(t0_a-tmin_a)*pow(x_a-(count1/2),2)+tmin_a;
    //calcualte time for B
    t_b = (4/(pow(count2,2)))*(t0_b-tmin_b)*pow(x_b-(count2/2),2)+tmin_b;
    //calcualte time for C
    t_c = (4/(pow(count3,2)))*(t0_c-tmin_c)*pow(x_c-(count3/2),2)+tmin_c;


    // movement of servo a (servo on the base)
    if(x_a <= count1) {
      if(millis() - a < t_a) {
        if(n-currval1 >= 0) {
          //target is bigger than currval
          servos[0].write(currval1+x_a);
        }
        else {
          //target is lower than currval
          servos[0].write(currval1-x_a);
        }
      }
      else {
        x_a+=1;
        a = millis();
        //Serial.println(t_a);
      }
    }

    // movement of servo b (servo on the bicept part of the arm)
    if(x_b <= count2) {
      if(millis() - b < t_b) {
        if(m-currval2 >= 0) {
          //target is bigger than currval
          servos[1].write(currval2+x_b);
        }
        else {
          //target is lower than currval
          servos[1].write(currval2-x_b);
        }
      }
      else {
        x_b+=1;
        b = millis();
        //Serial.println(t_b);
      }
    }

    // movement of servo c (servo of the tip angle, the gripper)
    if(x_c <= count3) {
      if(millis() - c < t_c) {
        if(gpos-currval3 >= 0) {
          //target is bigger than currval
          servos[2].write(currval3+x_c);
        }
        else {
          //target is lower than currval
          servos[2].write(currval3-x_c);
        }
      }
      else {
        x_c+=1;
        c = millis();
        //Serial.println(t_b);
      }
    }

    // if a new order (command from the RPi) came through, break the loop and go back to main loop
    if(order == 1) {
      break;
    }

    // if all the servos have ended its movement, break the loop.
    if(x_a >= count1 && x_b >= count2 && x_c >= count3) {
      break;
    }
  }
  Serial.print("values read from servo: ");
  curralpha=servos[0].read();
  currbeta=servos[1].read();
  Serial.print(curralpha); Serial.print(", "); Serial.println(currbeta);
  }



