import serial
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft
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
        self.recBuffer = collections.deque(maxlen=64)
        self.serial = serial.Serial()
        self.isSerialOpen = False
        self.isRun = False
        self.isReceiving = True
        self.serialPortNames = []
        self.scanports()
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0

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

    def getserialdata(self, frame, lines, lineValueText, lineLabel, timeText):
        while len(self.recBuffer) > 0:
            line = self.recBuffer.popleft()
            if len(line) == 16:
                currentTimer = time.perf_counter_ns()
                self.plotTimer = int((currentTimer - self.previousTimer) / 1000)  # the first reading will be erroneous
                self.previousTimer = currentTimer
                timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
                databytes = bytearray.fromhex(line)
                timedata = databytes[0:2]
                value, = struct.unpack('>h', timedata)
                self.data[0].append(value)
                for i in range(self.numPlots):
                    index = i + 1
                    sampledata = databytes[(index * self.dataNumBytes):(self.dataNumBytes + index * self.dataNumBytes)]
                    value, = struct.unpack('>h', sampledata)
                    self.data[index].append(value)
                    lines[i*2].set_data(range(self.plotLength), self.data[index])
                    lineValueText[i].set_text('[' + lineLabel[i] + '] = ' + str(value))
                    data = list(self.data[index])
                    #ham = np.hamming(len(data))
                    spec = abs(np.fft.fft(data))
                    lines[i*2+1].set_data(range(len(spec)), spec)



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
            line = self.serial.readline()
            decode = line.decode('utf8').rstrip()
            self.isReceiving = True
            self.recBuffer.append(decode)

    def close(self):
        self.isRun = False
        self.thread.join()
        self.serial.close()
        print("Data collection stopped\n")


def main():
    maxPlotLength = 300  # number of points in x-axis of real time plot
    dataNumBytes = 2  # number of bytes of 1 data point
    numPlots = 3  # number of plots in 1 graph
    baudRate = 2000000

    print("running serialplot as script\n")
    portnames = ['None']
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        portnames.append(port)

    if len(portnames) > 1:
        print("Found serial device\n")
        s = SerialPlot(serialPort=portnames[1], serialBaud=baudRate, numPlots=numPlots, dataNumBytes=dataNumBytes, plotLength=maxPlotLength)
    else:
        print("No serial devices found\n")


    s.serialStart()

    pltInterval = 100  # Period at which the plot animation updates [ms]
    xmin = 0
    xmax = maxPlotLength
    ymin = -(32767)
    ymax = 32767
    fig = plt.figure(figsize=(10, 10))
    axs = []
    for i in range(numPlots):
        ax = plt.subplot(3, 2, (i*2)+1)
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10))
        ax.set_xlabel("Time")
        ax.set_ylabel("Accel Output")
        axs.append(ax)
        axfft = plt.subplot(3, 2, (i*2)+2)
        axfft.set_xlabel("Frequency")
        axfft.set_ylabel("Magnitude")
        axfft.set_ylim(ymin, ymax)
        axfft.set_xlim(0, 100)
        axs.append(axfft)

    lineLabel = ['X', 'Y', 'Z']
    style = ['r-', 'c-', 'b-']  # linestyles for the different plots
    timeText = axs[0].text(0.70, 0.95, '', transform=axs[0].transAxes)
    lines = []
    lineValueText = []
    for i in range(numPlots):
        line, = axs[i*2].plot([], [], style[i], label=lineLabel[i])
        lines.append(line)
        lineValueText.append(axs[i*2].text(0.70, 0.90, '', transform=axs[i*2].transAxes))
        linefft, = axs[i*2+1].plot([], [], style[i], label=lineLabel[i])
        lines.append(linefft)

    anim = animation.FuncAnimation(fig, s.getserialdata, fargs=(lines, lineValueText, lineLabel, timeText), interval=pltInterval)  # fargs has to be a tuple
    plt.legend(loc="upper left")
    plt.show()

    s.close()

    print("done")


if __name__ == "__main__":
    main()