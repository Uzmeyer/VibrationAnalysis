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
from datetime import datetime
import copy
import collections
import struct

class App(Frame):
    def __init__(self, figure, lines, master=None):
        frame = Tk.Frame(master)
        self.master = master
        self.figure = figure
        self.lines = lines
        self.recbuffer = []
        self.data = []
        self.fftdata = []
        self.datetime = ""
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
        self.thread = None
        self.isRun = False
        self.isCapturing = False
        self.dataProcessed = True
        self.captureComplete = False
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
        ser = self.serialselect.get()
        self.setserial(ser)
        self.serialselect.bind('<<ComboboxSelected>>', self.serialChanged)

        labelBaud = Label(self.master, text="Select BAUD")
        labelBaud.grid(column=1, row=0)

        self.baudselect = Combobox(self.master)
        self.baudselect['values'] = self.bauds
        self.baudselect.grid(column=1, row=1)
        self.baudselect.current(0)
        baud = self.baudselect.get()
        self.setbaud(baud)
        self.baudselect.bind('<<ComboboxSelected>>', self.baudChanged)

        canvas = FigureCanvasTkAgg(figure, master=self.master)
        canvas.get_tk_widget().grid(column=1, row=2)

        #toolbar = NavigationToolbar2Tk(canvas, self.master)
        #toolbar.update()

        sendbutton = Button(self.master, text='Start', command=self.startcapture)
        sendbutton.grid(column=3, row=1)

    def plotdata(self, frame, lines, axs):
        if not self.dataProcessed:
            datafile = open((self.datetime + '_data.csv'), 'w+')
            fftfile = open((self.datetime + '_fft.csv'), 'w+')
            timevals = []
            xvals = []
            yvals = []
            zvals = []
            for sample in self.recbuffer:
                t, x, y, z = sample
                datafile.write(t + ',' + x + ',' + y + ',' + z + '\n')
                timevals.append(int(t))
                xvals.append(int(x))
                yvals.append(int(y))
                zvals.append(int(z))

            datafile.close()
            tmax = max(timevals)
            tmin = min(timevals)
            lims = []
            xmax = max(xvals) * 1.2
            xmin = min(xvals) * 1.2
            lims.append((xmin, xmax))
            ymax = max(yvals) * 1.2
            ymin = min(yvals) * 1.2
            lims.append((ymin, ymax))
            zmax = max(zvals) * 1.2
            zmin = min(zvals) * 1.2
            lims.append((zmin, zmax))
            self.data.clear()
            self.data.append(timevals)
            self.data.append(xvals)
            self.data.append(yvals)
            self.data.append(zvals)
            xfft = []
            yfft = []
            zfft = []
            self.fftdata.clear()
            self.fftdata.append(xfft)
            self.fftdata.append(yfft)
            self.fftdata.append(zfft)
            timesteps = []
            prevval = 0
            for i in timevals:
                timesteps.append(i - prevval)
                prevval = i

            timemean = np.mean(timesteps)
            timestdev = np.std(timesteps)
            print("Timestep mean is " + str(timemean) + ' and stdev is ' + str(timestdev))
            begintime = self.data[0][0] / 1000000 #microseconds to seconds
            endtime = self.data[0][-1] / 1000000 #microseconds to seconds
            samplinginterval = timemean / 1000000 #microseconds to seconds
            samplingFrequency = 1/samplinginterval
            #time = np.arrange(begintime, endtime, samplinginterval)

            for i in range(3):
                index = i + 1
                axs[i * 2].set_xlim(0, tmax)
                axs[i * 2].set_ylim(lims[i])
                lines[i * 2].set_data(self.data[0], self.data[index])
                data = np.array(self.data[index])
                #data = data - np.mean(data)
                fourierTransform = abs(np.fft.fft(data)/len(data)) #normalize
                spec = fourierTransform[0:int(len(data)/2)]
                tpCount = len(data)
                values = np.arange(int(tpCount / 2))
                timePeriod = tpCount / samplingFrequency
                frequencies = values / timePeriod
                smax = max(spec)
                smin = min(spec)
                axs[i * 2 + 1].set_xlim(0, len(frequencies))
                axs[i * 2 + 1].set_ylim(smin, smax)
                axs[i * 2 + 1].set_yscale('log')
                lines[i * 2 + 1].set_data(frequencies, spec)
                for f, s in zip(frequencies, spec):
                    fftfile.write(str(f) + ',' + str(s) + '\n')

            self.dataProcessed = True
            fftfile.close()

    def startcapture(self):
        if self.isCapturing:
            print("already running")
            return

        self.thread = Thread(target=self.capturethread)
        self.thread.start()
        while not self.isRun:
            time.sleep(0.1)

        self.serial.write(str.encode('s'))

    def capturethread(self):
        time.sleep(1)
        self.isRun = True
        self.captureComplete = False
        self.serial.reset_input_buffer()
        self.recbuffer.clear()
        while not self.captureComplete:
            line = self.serial.readline()
            decode = line.decode('utf8').rstrip()
            if not self.isCapturing:
                if decode == 'Start':
                    self.isCapturing = True
                    datetimeobj = datetime.now()
                    self.datetime = datetimeobj.strftime("%Y%m%d%H%M%S")
                continue
            else:
                if decode == 'Stop':
                    self.captureComplete = True
                    self.isCapturing = False
                    self.isRun = False
                    self.dataProcessed = False
                    return
                else:
                    print(decode)
                    t, x, y, z = decode.split(',')
                    self.recbuffer.append((t, x, y,  z))

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
                self.serialBaud = baud
                print('Connected to ' + str(self.serialPort) + ' at ' + str(self.serialBaud) + ' BAUD.')


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
    fig = plt.figure(figsize=(8, 8))
    axs = []
    for i in range(3):
        ax = plt.subplot(3, 2, (i * 2) + 1)
        ax.set_xlabel("Time")
        ax.set_ylabel("Accel Output")
        axs.append(ax)
        axfft = plt.subplot(3, 2, (i * 2) + 2)
        axfft.set_xlabel("Frequency")
        axfft.set_ylabel("Magnitude")
        axs.append(axfft)

    lineLabel = ['X', 'Y', 'Z']
    style = ['r-', 'c-', 'b-']  # linestyles for the different plots
    lines = []
    lineValueText = []
    for i in range(3):
        line, = axs[i * 2].plot([], [], style[i], label=lineLabel[i])
        lines.append(line)
        lineValueText.append(axs[i * 2].text(0.70, 0.90, '', transform=axs[i * 2].transAxes))
        linefft, = axs[i * 2 + 1].plot([], [], style[i], label=lineLabel[i])
        lines.append(linefft)

    root = Tk.Tk()
    app = App(fig, lines, root)
    anim = animation.FuncAnimation(fig, app.plotdata, fargs=(lines, axs), interval=1000)
    root.mainloop()


if __name__ == "__main__":
    main()