import tkinter as tk
import time
import os
import errno
import threading
import sys
import subprocess
import signal
import psutil
from dataConversion import encodeA429, decodeA429, encodeAfdx, decodeAfdx
  
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
        self.angleOfAttack_rt = tk.Label(root, font = ('calibre', 10, 'bold'))
        self.verticalSpeed_rt = tk.Label(root, font = ('calibre', 10, 'bold'))
        self.error_label = tk.Label(root, textvariable = self.error_field, font = ('calibre', 10, 'bold'), fg = "red")
        self.avionicsUnit_rt = tk.Label(root, font = ('calibre', 10, 'bold'))

        # Inputs
        self.altitude = 0
        self.angleOfAttack = 0
        self.verticalSpeed = 0
        self.avionicsUnit = "AU_SOL"
        
    # Init Input Fields
    def initInputFields(self):
        self.altitude_field = tk.StringVar()
        self.angleOfAttack_field = tk.StringVar()
        self.verticalSpeed_field = tk.StringVar()
        self.avionicsUnit_field = tk.StringVar()
        self.error_field = tk.StringVar()

        self.altitude_label = tk.Label(root, text = 'Altitude', font=('calibre', 10, 'bold'))
        self.altitude_entry = tk.Entry(root, textvariable = self.altitude_field, font=('calibre', 10, 'normal'))

        self.angleOfAttack_label = tk.Label(root, text = 'Angle Of Attack', font = ('calibre', 10, 'bold'))
        self.angleOfAttack_entry = tk.Entry(root, textvariable = self.angleOfAttack_field, font = ('calibre', 10, 'normal'))

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

        self.angleOfAttack_label.grid(row = 2, column = 0)
        self.angleOfAttack_entry.grid(row = 2, column = 1)
        self.angleOfAttack_rt.grid(row = 2, column = 2)

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

                temp = decodeA429(dataTab[0], "cal")
                decodedAltitude = temp["altitude"]
                decodedAngleOfAttack =  decodeA429(dataTab[1], "cal")["verticalSpeed"]
                decodedVerticalSpeed = decodeA429(dataTab[2], "cal")["angleOfAttack"]
                decodedAvionicsUnit = temp["avionicsUnit"]

                self.altitude = decodedAltitude
                self.angleOfAttack = decodedAngleOfAttack
                self.verticalSpeed = decodedVerticalSpeed
                self.avionicsUnit = decodedAvionicsUnit

    # Updates the Gui
    def update(self):
        self.readCalculatorData()
        self.altitude_rt.configure(text = '{} ft'.format(self.altitude))
        self.avionicsUnit_rt.configure(text = '{}'.format(self.avionicsUnit))
        self.angleOfAttack_rt.configure(text = '{} °'.format(self.angleOfAttack))
        self.verticalSpeed_rt.configure(text = '{} fpm'.format(self.verticalSpeed))
        self.altitude_rt.after(100, self.update)

    # Submit values to Calculator
    def submit(self):
        altitude = self.altitude_field.get()
        angleOfAttack = self.angleOfAttack_field.get()
        verticalSpeed = self.verticalSpeed_field.get()

        altitudeEmpty = True if len(altitude) == 0 else False
        angleOfAttackEmpty = True if len(angleOfAttack) == 0 else False
        verticalSpeedEmpty = True if len(verticalSpeed)  == 0 else False

        if (not altitudeEmpty and (not angleOfAttackEmpty or not angleOfAttackEmpty)):
            self.error_field.set("You should provide Altitude \n or Angle Of Attack and Vertical Speed")
            return
        elif ((not angleOfAttackEmpty and verticalSpeedEmpty) or (verticalSpeedEmpty and not verticalSpeedEmpty)):
            self.error_field.set("You should provide Altitude \n or Angle Of Attack and Vertical Speed")
            return
        elif (altitudeEmpty and angleOfAttackEmpty and verticalSpeedEmpty):
            self.error_field.set("You should provide Altitude \n or Angle Of Attack and Vertical Speed")
            return

        altitude_num = int(altitude) if altitude != "" else 0
        angleOfAttack_num = int(angleOfAttack) if angleOfAttack != "" else 0
        verticalSpeed_num = int(verticalSpeed) if verticalSpeed != "" else 0
        
        if (altitude_num > 40000 or altitude_num < 0):
            self.error_field.set("Altitude has to be \n between 0 and 40000")
            return
        elif (angleOfAttack_num > 16 or angleOfAttack_num < -16):
            self.error_field.set("Angle Of Attack has to be \n between 0 and 100")
            return
        elif (verticalSpeed_num > 800 or verticalSpeed_num < 0):
            self.error_field.set("Vertical Speed has to be \n between 0 and 800")
            return
        else:
            self.error_field.set("")

        os.kill(childPid, signal.SIGUSR1)

        with open('/tmp/interfaceToCalculator', 'w') as f:
            if random.uniform(0, 1) > 0.5: # simulate data arriving at different moments 
                f.write("{},{},{}".format(encodeA429("agr", 1, "", altitude_num), encodeA429("agr", 2, "", angleOfAttack_num), encodeA429("agr", 3, "", verticalSpeed_num)))
                f.write("{},{},{}".format(encodeAfdx("agr", 1, "", altitude_num), encodeAfdx("agr", 2, "", angleOfAttack_num), encodeAfdx("agr", 3, "", verticalSpeed_num)))
            else:
                f.write("{},{},{}".format(encodeAfdx("agr", 1, "", altitude_num), encodeAfdx("agr", 2, "", angleOfAttack_num), encodeAfdx("agr", 3, "", verticalSpeed_num)))
                f.write("{},{},{}".format(encodeA429("agr", 1, "", altitude_num), encodeA429("agr", 2, "", angleOfAttack_num), encodeA429("agr", 3, "", verticalSpeed_num)))

root = tk.Tk()
root.geometry("800x400")
root.title("Panneau de controle")

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=2)
root.columnconfigure(2, weight=2)

this_proc = os.getpid()

for proc in psutil.process_iter():
    procd = proc.as_dict(attrs=['pid', 'name'])
    if "python" in str(procd['name']) and procd['pid'] != this_proc:
        proc.kill()

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