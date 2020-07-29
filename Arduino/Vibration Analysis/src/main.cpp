#include <Arduino.h>

long data = 0;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.print("Starting...\n");
  randomSeed(analogRead(0));
}

void loop() {
  // put your main code here, to run repeatedly:
  data = random(-100, 100);
  Serial.println(data);
  delay(500);
}