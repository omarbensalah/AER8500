
import tkinter as tk
import time
  
class Interface:
    def __init__(self, master):
        self.altitude_var = tk.StringVar()
        self.enginePower_var = tk.StringVar()
        self.verticalSpeed_var = tk.StringVar()

        self.altitude_label = tk.Label(root, text = 'Altitude', font=('calibre', 10, 'bold'))
        self.altitude_entry = tk.Entry(root, textvariable = self.altitude_var, font=('calibre', 10, 'normal'))
        self.altitude_rt = tk.Label(root, text = '500', font=('calibre', 10, 'bold'))
        
        self.enginePower_label = tk.Label(root, text = 'Engine Power', font = ('calibre', 10, 'bold'))
        self.enginePower_entry = tk.Entry(root, textvariable = self.enginePower_var, font = ('calibre', 10, 'normal'))
        self.enginePower_rt = tk.Label(root, text = '50%', font = ('calibre', 10, 'bold'))

        self.verticalSpeed_label = tk.Label(root, text = 'Vertical Speed', font = ('calibre', 10, 'bold'))
        self.verticalSpeed_entry = tk.Entry(root, textvariable = self.verticalSpeed_var, font = ('calibre', 10, 'normal'))
        self.verticalSpeed_rt = tk.Label(root, text = '2500 fpm', font = ('calibre', 10, 'bold'))
        
        self.sub_btn=tk.Button(root, text = 'Submit', command = self.submit)

        self.metric_label = tk.Label(root, text = 'Metric', font=('calibre', 10, 'bold'))
        self.wantedValue_label = tk.Label(root, text = 'Wanted Value', font = ('calibre', 10, 'bold'))
        self.actualValue_label = tk.Label(root, text = 'Actual Value', font = ('calibre', 10, 'bold'))

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

        self.count = 0
        self.update_label()

    def update_label(self):
        self.altitude_rt.configure(text = '{} ft'.format(self.count))
        self.altitude_rt.after(500, self.update_label)
        self.count += 1

    def submit(self):
        altitude = self.altitude_var.get()
        enginePower = self.enginePower_var.get()
        verticalSpeed = self.verticalSpeed_var.get()
        
        print("The Altitude is : " + altitude)
        print("The Engine Power is : " + enginePower)
        print("The Vertical Speed is : " + verticalSpeed)
        
        self.altitude_var.set("")
        self.enginePower_var.set("")
        self.verticalSpeed_var.set("")        

root = tk.Tk()
root.geometry("350x200")
Interface(root)
root.mainloop()