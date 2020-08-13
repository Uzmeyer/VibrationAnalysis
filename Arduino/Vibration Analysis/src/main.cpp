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

MPU6050 accelgyro;
long data = 0;
long i = 0;
bool blinkState = false;


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
  accelgyro.getAcceleration(&ax, &ay, &az);


  #ifdef OUTPUT_BINARY_ACCELGYRO
        Serial.write(sbyte1); 
        Serial.write(sbyte2);
        Serial.write((uint8_t)(ax >> 8)); Serial.write((uint8_t)(ax & 0xFF));
        Serial.write((uint8_t)(ay >> 8)); Serial.write((uint8_t)(ay & 0xFF));
        Serial.write((uint8_t)(az >> 8)); Serial.write((uint8_t)(az & 0xFF));
        Serial.write((uint8_t)(gx >> 8)); Serial.write((uint8_t)(gx & 0xFF));
        Serial.write((uint8_t)(gy >> 8)); Serial.write((uint8_t)(gy & 0xFF));
        Serial.write((uint8_t)(gz >> 8)); Serial.write((uint8_t)(gz & 0xFF));
  #endif
  
  i++;
  blinkState = !blinkState;
  digitalWrite(LED_PIN, blinkState);
  delay(100);
}