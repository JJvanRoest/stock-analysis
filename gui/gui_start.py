import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import logging


import tkinter as tk
from tkinter import ttk, Tk, Label, Button, W, Scale, HORIZONTAL

LARGE_FONT = ("Verdana", 12)

class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        master.title("Stock Analysis - BIT F4E")

        self.label = Label(master, text="This is our first GUI!")
        # self.label.pack()

        self.greet_button = Button(master, text="Greet", command=self.greet)
        # self.greet_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        # self.close_button.pack()
        
        self.scale = Scale(master, from_= 0, to = 10, resolution = 0.1, command = self.val, orient = HORIZONTAL)

        self.label.grid(columnspan=2, sticky=W)
        self.greet_button.grid(row=1)
        self.close_button.grid(row=1, column=1)
        self.scale.grid(columnspan=4)
    
    def val(self, value):
        print(value)


    def greet(self):
        logging.info("Greetings!")



if __name__ == "__main__":
    root = Tk()
    my_gui = MyFirstGUI(root)
    root.mainloop()