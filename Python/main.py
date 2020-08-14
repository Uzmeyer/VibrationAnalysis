import numpy as np
import serial
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation

from tkinter import *
from tkinter.ttk import *
import serial.tools.list_ports

from threading import Thread

import serialplot

plt.use("TkAgg")

ports = serial.tools.list_ports.comports()
portnames = ['None']
currentport = 'None'
bauds = [
         9600,
         19200,
         38400,
         57600,
         115200,
         460800,
         1500000,
         2000000
         ]
currentbaud = 460800

for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))
        portnames.append(port)


ser = serial.Serial()


class Window(Frame):
    def __init__(self, figure, master, SerialReference):
        Frame.__init__(self, master)
        self.entry = None
        self.setPoint = None
        self.master = master  # a reference to the master window
        self.serialReference = SerialReference  # keep a reference to our serial connection so that we can use it for bi-directional communicate from this class
        self.initWindow(figure)  # initialize the window with our settings

    def initWindow(self, figure):
        self.master.title("Real Time Plot")
        canvas = FigureCanvasTkAgg(figure, master=self.master)
        toolbar = NavigationToolbar2Tk(canvas, self.master)
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # create out widgets in the master frame
        lbl1 = Tk.Label(self.master, text="Scaling Factor")
        lbl1.pack(padx=5, pady=5)
        self.entry = Tk.Entry(self.master)
        self.entry.insert(0, '1.0')  # (index, string)
        self.entry.pack(padx=5)
        SendButton = Tk.Button(self.master, text='Send', command=self.sendFactorToMCU)
        SendButton.pack(padx=5)

    def sendFactorToMCU(self):
        self.serialReference.sendSerialData(self.entry.get() + '%')     # '%' is our ending marker



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


#selectSerial(ser, portnames[1])
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

