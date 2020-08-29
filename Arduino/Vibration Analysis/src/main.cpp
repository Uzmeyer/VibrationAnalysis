#include <Arduino.h>
#include <I2Cdev.h>
#include "MPU6050.h"

// Arduino Wire library is required if I2Cdev I2CDEV_ARDUINO_WIRE implementation
// is used in I2Cdev.h
#if (I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE) && !defined (PARTICLE)
    #include "Wire.h"
#endif

// class default I2C address is 0x68
// specific I2C addresses may be passed as a parameter here
// AD0 low = 0x68 (default for InvenSense evaluation board)
// AD0 high = 0x69

int16_t ax, ay, az;
int16_t gx, gy, gz;
uint8_t sbyte1 = 0b11111111;
uint8_t sbyte2 = 0b01010101;

// uncomment "OUTPUT_READABLE_ACCELGYRO" if you want to see a tab-separated
// list of the accel X/Y/Z and then gyro X/Y/Z values in decimal. Easy to read,
// not so easy to parse, and slow(er) over UART.
#define OUTPUT_READABLE_ACCELGYRO

// uncomment "OUTPUT_BINARY_ACCELGYRO" to send all 6 axes of data as 16-bit
// binary, one right after the other. This is very fast (as fast as possible
// without compression or data loss), and easy to parse, but impossible to read
// for a human.
#define OUTPUT_BINARY_ACCELGYRO

#define LED_PIN 13 // (Arduino is 13, Teensy is 11, Teensy++ is 6)
#define TIMEBYTES 2
#define DATACHANNELS 2
#define BYTESPERCHANNEL 2
#define DATABYTES DATACHANNELS*BYTESPERCHANNEL
#define STRDELIMS 2
#define DATALEN TIMEBYTES + DATABYTES
#define STRLEN 2 * (TIMEBYTES + DATABYTES) + STRDELIMS
MPU6050 accelgyro;
long data = 0;
uint16_t loopTime = 1000; //microseconds
unsigned long timer = 0;
bool blinkState = false;
uint8_t databuffer[8];
char sendbuffer[17];

void array_to_string(byte array[], unsigned int len, char buffer[])
{
    for (unsigned int i = 0; i < len; i++)
    {
        byte nib1 = (array[i] >> 4) & 0x0F;
        byte nib2 = (array[i] >> 0) & 0x0F;
        buffer[i*2+0] = nib1  < 0xA ? '0' + nib1  : 'A' + nib1  - 0xA;
        buffer[i*2+1] = nib2  < 0xA ? '0' + nib2  : 'A' + nib2  - 0xA;
    }
    buffer[len*2] = '\n';
    //buffer[len*2 + 1] = '\0';
}

void timeSync(unsigned long deltaT)
{
  unsigned long currTime = micros();
  long timeToDelay = deltaT - (currTime - timer);
  if (timeToDelay > 5000)
  {
    delay(timeToDelay / 1000);
    delayMicroseconds(timeToDelay % 1000);
  }
  else if (timeToDelay > 0)
  {
    delayMicroseconds(timeToDelay);
  }
  else
  {
      // timeToDelay is negative so we start immediately
  }
  timer = currTime + timeToDelay;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(2000000);
  Serial.print("Starting...\n");
  // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif
  
  Serial.println("Initializing I2C devices...");
  accelgyro.initialize();
  Serial.println("Testing device connections...");
  Serial.println(accelgyro.testConnection() ? "MPU6050 connection successful" : "MPU6050 connection failed");
  Serial.print("Current Bandwith config: ");
  Serial.println(accelgyro.getDLPFMode());
  accelgyro.setDLPFMode(MPU6050_DLPF_BW_256);
  Serial.print("Current Accel FullScale config: ");
  Serial.println(accelgyro.getFullScaleAccelRange());


  pinMode(LED_PIN, OUTPUT);

  randomSeed(analogRead(0));
  
}

void loop() {
  // put your main code here, to run repeatedly:
  timeSync(loopTime);
  accelgyro.getAcceleration(&ax, &ay, &az);
  databuffer[0] = timer >> 8;
  databuffer[1] = timer & 0xFF;
  databuffer[2] = ax >> 8;
  databuffer[3] = ax & 0xFF;
  databuffer[4] = ay >> 8;
  databuffer[5] = ay & 0xFF;
  databuffer[6] = az >> 8;
  databuffer[7] = az & 0xFF;
  array_to_string(databuffer, 8, sendbuffer);
  Serial.write(sendbuffer, 17);
  

  blinkState = !blinkState;
  digitalWrite(LED_PIN, blinkState);
  delay(1);
}