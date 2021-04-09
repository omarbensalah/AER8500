import Tkinter as tk
import time
import os
import errno
import threading
import sys
import subprocess
import signal

  
class Interface:
    def __init__(self, master):
        self.initInputFields()
        self.initOutputs()
        self.initStaticElements()
        self.positionElementsOnGridGui()

        self.update()


    # Init Fields and values of outputs
    def initOutputs(self):
        # Fields
        self.altitude_rt = tk.Label(root, font=('calibre', 10, 'bold'))
        self.enginePower_rt = tk.Label(root, font = ('calibre', 10, 'bold'))
        self.verticalSpeed_rt = tk.Label(root, font = ('calibre', 10, 'bold'))
        self.error_label = tk.Label(root, textvariable = self.error_field, font = ('calibre', 10, 'bold'), fg = "red")
        self.avionicsUnit_rt = tk.Label(root, font = ('calibre', 10, 'bold'))

        # Inputs
        self.altitude = 0
        self.enginePower = 0
        self.verticalSpeed = 0
        self.avionicsUnit = "AU_SOL"
        
    # Init Input Fields
    def initInputFields(self):
        self.altitude_field = tk.StringVar()
        self.enginePower_field = tk.StringVar()
        self.verticalSpeed_field = tk.StringVar()
        self.avionicsUnit_field = tk.StringVar()
        self.error_field = tk.StringVar()

        self.altitude_label = tk.Label(root, text = 'Altitude', font=('calibre', 10, 'bold'))
        self.altitude_entry = tk.Entry(root, textvariable = self.altitude_field, font=('calibre', 10, 'normal'))

        self.enginePower_label = tk.Label(root, text = 'Engine Power', font = ('calibre', 10, 'bold'))
        self.enginePower_entry = tk.Entry(root, textvariable = self.enginePower_field, font = ('calibre', 10, 'normal'))

        self.verticalSpeed_label = tk.Label(root, text = 'Vertical Speed', font = ('calibre', 10, 'bold'))
        self.verticalSpeed_entry = tk.Entry(root, textvariable = self.verticalSpeed_field, font = ('calibre', 10, 'normal'))

    # Init UI static elements: First row with columns titles
    def initStaticElements(self):
        self.metric_label = tk.Label(root, text = 'Metric', font=('calibre', 10, 'bold'))
        self.wantedValue_label = tk.Label(root, text = 'Wanted Value', font = ('calibre', 10, 'bold'))
        self.actualValue_label = tk.Label(root, text = 'Actual Value', font = ('calibre', 10, 'bold'))
        self.sub_btn=tk.Button(root, text = 'Submit', command = self.submit)

    # Position Elements on GUI
    def positionElementsOnGridGui(self):
        self.metric_label.grid(row = 0, column = 0)
        self.wantedValue_label.grid(row = 0, column = 1)
        self.actualValue_label.grid(row = 0, column = 2)

        self.altitude_label.grid(row = 1, column = 0)
        self.altitude_entry.grid(row = 1, column = 1)
        self.altitude_rt.grid(row = 1, column = 2)

        self.enginePower_label.grid(row = 2, column = 0)
        self.enginePower_entry.grid(row = 2, column = 1)
        self.enginePower_rt.grid(row = 2, column = 2)

        self.verticalSpeed_label.grid(row = 3, column = 0)
        self.verticalSpeed_entry.grid(row = 3, column = 1)
        self.verticalSpeed_rt.grid(row = 3, column = 2)

        self.sub_btn.grid(row = 5, column = 1)

        self.error_label.grid(row = 6, column = 1)
        self.avionicsUnit_rt.grid(row = 7, column = 1)

    # Reads data from pipe
    def readCalculatorData(self):
        try:
            os.mkfifo('/tmp/calculatorToInterface')
        except OSError as oe: 
            if oe.errno != errno.EEXIST:
                raise

        with open('/tmp/calculatorToInterface') as fifo:
            while True:
                data = fifo.read()
                if len(data) == 0:
                    break
                dataTab = data.split(",")
                self.altitude = dataTab[0]
                self.enginePower = dataTab[1]
                self.verticalSpeed = dataTab[2]
                self.avionicsUnit = dataTab[3]

    # Updates the Gui
    def update(self):
        self.readCalculatorData()
        self.altitude_rt.configure(text = '{} ft'.format(self.altitude))
        self.avionicsUnit_rt.configure(text = '{}'.format(self.avionicsUnit))
        self.enginePower_rt.configure(text = '{} %'.format(self.enginePower))
        self.verticalSpeed_rt.configure(text = '{} fpm'.format(self.verticalSpeed))
        self.altitude_rt.after(500, self.update)

    # Submit values to Calculator
    def submit(self):
        altitude = self.altitude_field.get()
        enginePower = self.enginePower_field.get()
        verticalSpeed = self.verticalSpeed_field.get()

        altitudeEmpty = True if len(altitude) == 0 else False
        enginePowerEmpty = True if len(enginePower) == 0 else False
        verticalSpeedEmpty = True if len(verticalSpeed)  == 0 else False

        if (not altitudeEmpty and (not enginePowerEmpty or not enginePowerEmpty)):
            self.error_field.set("You should provide Altitude \n or Engine Power and Vertical Speed")
            return
        elif ((not enginePowerEmpty and verticalSpeedEmpty) or (verticalSpeedEmpty and not verticalSpeedEmpty)):
            self.error_field.set("You should provide Altitude \n or Engine Power and Vertical Speed")
            return
        elif (altitudeEmpty and enginePowerEmpty and verticalSpeedEmpty):
            self.error_field.set("You should provide Altitude \n or Engine Power and Vertical Speed")
            return

        altitude_num = int(altitude) if altitude != "" else 0
        enginePower_num = int(enginePower) if enginePower != "" else 0
        verticalSpeed_num = int(verticalSpeed) if verticalSpeed != "" else 0
        
        if (altitude_num > 40000 or altitude_num < 0):
            self.error_field.set("Altitude has to be \n between 0 and 40000")
            return
        elif (enginePower_num > 100 or enginePower_num < 0):
            self.error_field.set("Engine Power has to be \n between 0 and 100")
            return
        elif (verticalSpeed_num > 800 or verticalSpeed_num < 0):
            self.error_field.set("Vertical Speed has to be \n between 0 and 800")
            return
        else:
            self.error_field.set("")

        os.kill(childPid, signal.SIGUSR1)

        with open('/tmp/interfaceToCalculator', 'w') as f:
            f.write("{},{},{}".format(altitude,enginePower,verticalSpeed))

root = tk.Tk()
root.geometry("800x400")
root.title("Panneau de controle")

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=2)
root.columnconfigure(2, weight=2)

if os.path.exists('/tmp/interfaceToCalculator'):
    os.remove('/tmp/interfaceToCalculator')

if os.path.exists('/tmp/calculatorToInterface'):
    os.remove('/tmp/calculatorToInterface')

childPid = os.fork()
if childPid == 0:
    exec(open('calculator.py').read())
else:
    Interface(root)
    root.mainloop()