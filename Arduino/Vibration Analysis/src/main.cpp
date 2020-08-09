#include <Arduino.h>
#include <Adafruit_MPU6050.h>

long data = 0;
long i = 0;

Adafruit_MPU6050 mpu;
Adafruit_Sensor *mpu_temp, *mpu_accel, *mpu_gyro;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(2000000);
  Serial.print("Starting...\n");
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  randomSeed(analogRead(0));
  Serial.println("MPU6050 Found!");
  mpu_temp = mpu.getTemperatureSensor();
  mpu_temp->printSensorDetails();

  mpu_accel = mpu.getAccelerometerSensor();
  mpu_accel->printSensorDetails();

  mpu_gyro = mpu.getGyroSensor();
  mpu_gyro->printSensorDetails();
}

void loop() {
  // put your main code here, to run repeatedly:
  sensors_event_t accel;
  mpu_accel->getEvent(&accel);

  /* Display the results (acceleration is measured in m/s^2) */
  Serial.print(i);
  Serial.print(",");
  Serial.print(accel.acceleration.x);
  Serial.print(",");
  Serial.print(accel.acceleration.y);
  Serial.print(",");
  Serial.print(accel.acceleration.z);
  Serial.print("\n");
  i++;
  delay(100);
}