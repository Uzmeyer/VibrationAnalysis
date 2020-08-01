import numpy as np
import serial
import matplotlib as plt
from tkinter import *
from tkinter.ttk import *
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
portnames = ['None']
currentport = 'None'
bauds = [
         9600,
         19200,
         38400,
         57600,
         115200
         ]
currentbaud = 115200

for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        portnames.append(port)


ser = serial.Serial()

def selectSerial(ser, port='None', baud=115200):
    ser.close()
    if port == 'None':
        return
    ser.baudrate = baud
    ser.port = port
    ser.open()
    return


def serialChanged(event):
    global currentport
    global currentbaud
    currentport = serialselect.get()
    currentbaud = baudselect.get()
    selectSerial(ser, currentport, currentbaud)
    return


selectSerial(ser, portnames[1])
print("hello")

window = Tk()
window.title('Vibration Analysis Logger')
window.geometry('350x200')

labelCom = Label(window, text="Select COM port")
labelCom.grid(column=0, row=0)

serialselect = Combobox(window)
serialselect['values'] = portnames
serialselect.grid(column=0, row=1)
serialselect.current(0)
serialselect.bind('<<ComboboxSelected>>', serialChanged)

labelBaud = Label(window, text="Select BAUD")
labelBaud.grid(column=1, row=0)

baudselect = Combobox(window)
baudselect['values'] = bauds
baudselect.grid(column=1, row=1)
baudselect.current(0)
baudselect.bind('<<ComboboxSelected>>', serialChanged)

window.mainloop()

while True:
    data = ser.readline()
    print(data)