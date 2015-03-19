#include <Herkulex.h>
#include <Servo.h>

int n=253; //motor ID - verify your ID !!!!
int m=252;
int incoming = 0, corrected = 0, xpos = 0, ypos = 0;
    
void setup()  
{

  delay(2000);  //a delay to have time for serial monitor opening
  Serial.begin(115200);    // Open serial communications
//   Serial.println("Begin");
  Herkulex.beginSerial1(115200); //open serial port 1 

  Herkulex.reboot(n); //reboot first motor
  Herkulex.reboot(m); // reboot second motor
  delay(500); // pause to let everything settle

  Herkulex.initialize(); //initialize motors
  delay(200); // pause to let everything settle

  Herkulex.moveOneAngle(n, 0, 1000, LED_BLUE); //move motor to origin
  Herkulex.moveOneAngle(m, 0, 1000, LED_BLUE); //move motor to origin
  
  
}

void readSerial()
{
  int i = 0;
  while (Serial.available() > 0)
  {
    do  
    {
      i = Serial.read();
      
    } while (i != 'B'); // end do-while
    xpos = Serial.parseInt();
    ypos = Serial.parseInt();
    if (Serial.read() == '\n')
    {
      return;
    } // end if
  } // end while
}


void loop(){
  
      // test serial control:
      // corrected equals incoming divided by 2, minus 160
      // incoming signal is between 0 & 640 (639?)
      // motor angle is -158 to +158

      // read serial
  readSerial ();

  corrected = ((xpos / 2) - 160);
//  Serial.println(incoming);
  Herkulex.moveOneAngle(m, corrected, 100, LED_BLUE); // move motor to the angle based on screen position
  
}
