// cobbled together by Marcus Blaisdell, this works for the main joystick lever
// but does not read the push buttons, still need to figure that one out
// suspect it has something to do with the addresses currently set in "trigger" 
// and j_stick

#include <Herkulex.h>
#include <Servo.h>
#include <SPI.h>

// Servo declaration, required to use analog servos
Servo myservo;

  // variables:
  
int potpin = 0, pot_val = 0, servo_val = 0;
int n=253; //motor ID - verify your ID !!!!
int m=252; // motor 2 ID
float cur_angle = 0, new_angle = 0;
    
void setup()  
{
  delay(2000);  //a delay to have time for serial monitor opening
  Serial.begin(115200);    // Open serial communications
  Serial.println("Begin");
    
    //use the Herkulex library for Herkulex smart servo comms
    
  Herkulex.beginSerial1(115200); //open serial port 1 
  Herkulex.reboot(n); //reboot first motor
  Herkulex.reboot(m); // reboot second motor
  delay(500); 
  
  Herkulex.initialize(); //initialize motors
  delay(200);
  
    // move each motor to initial position (should be zero degrees, straight up)
    
  Herkulex.moveOneAngle(n, cur_angle, 1000, LED_BLUE); //move motor
  Herkulex.moveOneAngle(m, cur_angle, 1000, LED_BLUE); //move motor
}


void loop()
{
  // declare variables
  
  int up_button = 3;
  int down_button = 4;
  
    // set pin mode on each button
  pinMode (up_button, INPUT);
  pinMode (down_button, INPUT);

// joystick stuff, uses SPI, Serial Peripheral Interface

   SPI.begin();                             //  Initialize SPI parameters
   SPI.setBitOrder(MSBFIRST);               //  MSB to be sent first
   SPI.setDataMode(SPI_MODE0);              //  Set for clock rising edge
   SPI.setClockDivider(SPI_CLOCK_DIV64);    //  Set clock divider (optional)
   
     //  Set SPI pins to be outputs
     
   int S_Select = 53;
   pinMode(S_Select, OUTPUT);               

   int val = 0;                             //  “val” is a test variable used when reading pins

    // since we're using SPI, we need to setup the address and a ??
    
   byte trigger = B10000011;
   byte j_stick = B00000000;
      
      
   digitalWrite(S_Select,LOW);              // Drop SPI chip-select to 0 (Arduino pin 10)
   SPI.transfer(0x00);
   SPI.transfer(trigger);                   // Do SPI transfer of variable pot

   j_stick = SPI.transfer(0x00);
   digitalWrite(S_Select,HIGH);             // Raise chip-select to 1
   SPI.end();

    // open a serial port to communicate with the joystick:
    
   Serial.begin(57600);
   Serial.println (j_stick);
   Serial.end();

    // read data from the joystick and decode it:
    // each movement of the joystick adjusts two potentiometers that determines an analog value that is 
    // sent to the arduino, by trial and error, we found rough numbers that determine direction


    // if you move the joystick left, cause both motors to move in one direction,
    // if you move the joystick right, both motors move in the opposite direction
    
  if (j_stick > 158 && j_stick < 172)
  {
    cur_angle--;
  Herkulex.moveOneAngle(n, cur_angle, 100, LED_GREEN);  //move motor (motors are facing each other (opposed))
  Herkulex.moveOneAngle(m, -cur_angle, 100, LED_GREEN); //move motor (moving 1 in one direction and the other)
  delay(10);                                            // in the opposite will cause them to move in the same 
  }                                                     // effective direction nearly simultaneously
                                                        // there is another command in the Herkulex library
                                                        // that will sync two motors movement, you should use 
                                                        // that instead of controlling each individually
  if (j_stick > 13 && j_stick < 27)
  {
    cur_angle++;
  Herkulex.moveOneAngle(n, cur_angle, 100, LED_BLUE); //move motor
  Herkulex.moveOneAngle(m, -cur_angle, 100, LED_BLUE); //move motor
  delay(10);
  }
}
