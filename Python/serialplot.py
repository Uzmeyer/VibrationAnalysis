import serial
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation

import serial.tools.list_ports

from threading import Thread
import time


class SerialPlot:
    def __init__(self, serialPort='None', serialBaud=115200, plotLength=100, dataNumBytes=2, numPlots=1):
        self.serialPort = serialPort
        self.serialBaud = serialBaud
        self.plotLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.numPlots = numPlots
        self.serial = serial.Serial()
        self.isSerialOpen = False
        self.serialPortNames = []
        self.scanports()
        self.thread = None

        self.setbaud(serialBaud)
        self.setserial(serialPort)

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

    def scanports(self):
        serialports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(serialports):
            print("{}: {} [{}]".format(port, desc, hwid))
            self.serialPortNames.append(port)

    def serialStart(self):
        print("test")


if __name__ == "__main__":
    print("running serialplot as script\n")
    portnames = ['None']
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        portnames.append(port)

    if len(portnames) > 1:
        print("Found serial device\n")
        s = SerialPlot(serialPort=portnames[1])
    else:
        print("No serial devices found\n")
