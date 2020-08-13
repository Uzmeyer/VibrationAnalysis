import serial
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation

import serial.tools.list_ports

from threading import Thread
import time
import copy
import collections
import struct


class SerialPlot:
    def __init__(self, serialPort='None', serialBaud=115200, plotLength=100, dataNumBytes=2, numPlots=1):
        self.serialPort = serialPort
        self.serialBaud = serialBaud
        self.plotLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.numPlots = numPlots
        if dataNumBytes == 2:
            self.dataType = 'h'     # 2 byte integer
        elif dataNumBytes == 4:
            self.dataType = 'f'     # 4 byte float
        self.data = []
        self.data.append(collections.deque([0] * plotLength, maxlen=plotLength))  #time
        for i in range(self.numPlots):
            self.data.append(collections.deque([0] * plotLength, maxlen=plotLength))  #data
        self.rawData = bytearray(numPlots * dataNumBytes + 2 + 2)  #buffer for databytes + startbytes + timebytes
        self.recBuffer = collections.deque(maxlen=64)
        self.serial = serial.Serial()
        self.isSerialOpen = False
        self.isRun = False
        self.isReceiving = True
        self.serialPortNames = []
        self.scanports()
        self.thread = None
        self.sbyte1Found = False
        self.sbyte2Found = False
        self.messageLength = self.dataNumBytes * numPlots + 2
        self.message = bytearray(self.messageLength)
        self.bytesCollected = 0
        self.messages = []

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

    def getserialdata(self):
        while len(self.recBuffer) > 0:
            byte = self.recBuffer.popleft()
            if not self.sbyte1Found and not self.sbyte2Found:
                if byte != 255:
                    continue
                else:
                    self.sbyte1Found = True
                    continue
            elif self.sbyte1Found and not self.sbyte2Found:
                if byte == 85:
                    self.sbyte2Found = True
                    continue
                else:
                    self.sbyte1Found = False
                    continue
            elif self.bytesCollected < self.messageLength:
                self.message[self.bytesCollected] = byte
                self.bytesCollected += 1
                continue
            else:
                print(self.message)
                self.messages.append(self.message.copy())
                self.bytesCollected = 0
                self.sbyte1Found = False
                self.sbyte2Found = False

    def serialStart(self):
        if self.thread is None:
            self.isRun = True
            self.thread = Thread(target=self.datareadthread)
            self.thread.start()
            while self.isReceiving != True:
                time.sleep(0.1)

    def datareadthread(self):
        time.sleep(1)
        self.serial.reset_input_buffer()
        while self.isRun:
            self.serial.readinto(self.rawData)
            self.isReceiving = True
            privateData = copy.deepcopy(self.rawData)
            for byte in privateData:
                self.recBuffer.append(copy.deepcopy(byte))

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serial.close()
        print("Data collection stopped\n")


if __name__ == "__main__":
    print("running serialplot as script\n")
    portnames = ['None']
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        portnames.append(port)

    if len(portnames) > 1:
        print("Found serial device\n")
        s = SerialPlot(serialPort=portnames[1], serialBaud=2000000, numPlots=3)
    else:
        print("No serial devices found\n")

    s.serialStart()
    t_end = time.time() + 10
    while t_end > time.time():
        s.getserialdata()
    s.close()
    print("done")