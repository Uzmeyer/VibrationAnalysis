import serial
import matplotlib.pyplot as plt
import numpy as np
from numpy.ma import mask_cols
from scipy.fftpack import fft
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation

import serial.tools.list_ports

import tkinter as Tk
from tkinter.ttk import *
from tkinter.ttk import *
import serial.tools.list_ports

from threading import Thread
import time
import copy
import collections
import struct

class App(Frame):
    def __init__(self, figure, master=None):
        frame = Tk.Frame(master)
        self.master = master
        self.figure = figure
        self.serialPortNames = []
        self.bauds = [
            9600,
            19200,
            38400,
            57600,
            115200,
            460800,
            1500000,
            2000000
        ]
        self.serial = serial.Serial()
        self.isSerialOpen = False
        self.serialBaud = None
        self.serialselect = None
        self.baudselect = None
        self.scanports()
        self.initWindow(figure)

    def initWindow(self, figure):
        self.master.title('Vibration Analysis Logger')
        self.master.geometry('1200x1300')

        labelCom = Label(self.master, text="Select COM port")
        labelCom.grid(column=0, row=0)

        self.serialselect = Combobox(self.master)
        self.serialselect['values'] = self.serialPortNames
        self.serialselect.grid(column=0, row=1)
        self.serialselect.current(0)
        self.serialselect.bind('<<ComboboxSelected>>', self.serialChanged)

        labelBaud = Label(self.master, text="Select BAUD")
        labelBaud.grid(column=1, row=0)

        self.baudselect = Combobox(self.master)
        self.baudselect['values'] = self.bauds
        self.baudselect.grid(column=1, row=1)
        self.baudselect.current(0)
        self.baudselect.bind('<<ComboboxSelected>>', self.baudChanged)

        canvas = FigureCanvasTkAgg(figure, master=self.master)
        canvas.get_tk_widget().grid(column=1, row=2)

        sendbutton = Button(self.master, text='Start')
        sendbutton.grid(column=1, row=3)

    def scanports(self):
        serialports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(serialports):
            print("{}: {} [{}]".format(port, desc, hwid))
            self.serialPortNames.append(port)

    def setserial(self, serialPort='None'):
        if serialPort == 'None':
            self.serial.close()
            self.serialPort = 'None'
            self.isSerialOpen = False
            print("Selected no Serial Port\n")
            return

        if self.isSerialOpen:
            try:
                self.serial.close()
                self.serial.port = serialPort
                self.serial.open()
            except:
                print("Failed to connect with " + str(serialPort) + ' at ' + str(self.serialBaud) + ' BAUD.')
                self.setserial(self.serialPort)
            else:
                print('Connected to ' + str(serialPort) + ' at ' + str(self.serialBaud) + ' BAUD.')
                self.serialPort = serialPort

        else:
            try:
                self.serial.port = serialPort
                self.serial.open()
            except:
                print("Failed to connect with " + str(serialPort) + ' at ' + str(self.serialBaud) + ' BAUD.')
            else:
                print('Connected to ' + str(serialPort) + ' at ' + str(self.serialBaud) + ' BAUD.')
                self.serialPort = serialPort
                self.isSerialOpen = True

    def setbaud(self, baud=115200):
        if self.isSerialOpen:
            try:
                self.serial.close()
                self.serial.baudrate = baud
                self.serial.open()
            except:
                print("Failed to connect with " + str(self.serialPort) + ' at ' + str(self.serialBaud) + ' BAUD.')
                self.setbaud(self.baud)
            else:
                print('Connected to ' + str(self.serialPort) + ' at ' + str(self.serialBaud) + ' BAUD.')
                self.serialBaud = baud

        else:
            self.serial.baudrate = baud
            print("set BAUD to " + str(baud))
            self.serialBaud = baud

    def serialChanged(self, event):
        ser = self.serialselect.get()
        self.setserial(ser)
        return

    def baudChanged(self, event):
        baud = self.baudselect.get()
        self.setbaud(baud)
        return

    def __del__(self):
        self.master.destroy()


def main():
    fig = plt.figure(figsize=(10, 10))
    root = Tk.Tk()
    app = App(fig, root)
    root.mainloop()


if __name__ == "__main__":
    main()