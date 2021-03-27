import Tkinter as tk
import time
import os
import errno
import threading

  
class Interface:
    def __init__(self, master):
        self.altitude_field = tk.StringVar()
        self.enginePower_field = tk.StringVar()
        self.verticalSpeed_field = tk.StringVar()
        
        self.attitude_field = tk.StringVar()
        self.error_field = tk.StringVar()
        self.rtValue = 0

        self.altitude_label = tk.Label(root, text = 'Altitude', font=('calibre', 10, 'bold'))
        self.altitude_entry = tk.Entry(root, textvariable = self.altitude_field, font=('calibre', 10, 'normal'))
        self.altitude_rt = tk.Label(root, text = '500', font=('calibre', 10, 'bold'))
        
        self.enginePower_label = tk.Label(root, text = 'Engine Power', font = ('calibre', 10, 'bold'))
        self.enginePower_entry = tk.Entry(root, textvariable = self.enginePower_field, font = ('calibre', 10, 'normal'))
        self.enginePower_rt = tk.Label(root, text = '50%', font = ('calibre', 10, 'bold'))

        self.verticalSpeed_label = tk.Label(root, text = 'Vertical Speed', font = ('calibre', 10, 'bold'))
        self.verticalSpeed_entry = tk.Entry(root, textvariable = self.verticalSpeed_field, font = ('calibre', 10, 'normal'))
        self.verticalSpeed_rt = tk.Label(root, text = '2500 fpm', font = ('calibre', 10, 'bold'))
        
        self.sub_btn=tk.Button(root, text = 'Submit', command = self.submit)

        self.metric_label = tk.Label(root, text = 'Metric', font=('calibre', 10, 'bold'))
        self.wantedValue_label = tk.Label(root, text = 'Wanted Value', font = ('calibre', 10, 'bold'))
        self.actualValue_label = tk.Label(root, text = 'Actual Value', font = ('calibre', 10, 'bold'))

        self.error_label = tk.Label(root, textvariable = self.error_field, font = ('calibre', 10, 'bold'), fg = "red")
        self.attitude_label = tk.Label(root, textvariable = self.attitude_field, font = ('calibre', 10, 'bold'))

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
        self.attitude_label.grid(row = 7, column = 1)
        self.attitude_field.set("AU_SOL")

        self.update()
    
    def readCalculatorData(self):
        FIFO = '/tmp/bus'

        try:
            os.mkfifo(FIFO)
        except OSError as oe: 
            if oe.errno != errno.EEXIST:
                raise

        with open(FIFO) as fifo:
            while True:
                data = fifo.read()
                if len(data) == 0:
                    break
                self.rtValue = data

    def update(self):
        self.readCalculatorData()
        self.altitude_rt.configure(text = '{} ft'.format(self.rtValue))
        self.altitude_rt.after(500, self.update)

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
        
        print("The Altitude is : {}".format(altitude_num))
        print("The Engine Power is : {}".format(enginePower_num))
        print("The Vertical Speed is : {}".format(verticalSpeed_num))

root = tk.Tk()
root.geometry("800x400")
root.title("Panneau de controle")

root.columnconfigure(0, weight=2)
root.columnconfigure(1, weight=2)
root.columnconfigure(2, weight=2)

Interface(root)
root.mainloop()