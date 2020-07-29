import numpy as np
import serial

ser = serial.Serial('COM4', 115200)

print("hello")

while True:
    data = ser.readline()
    print(data)