from tkinter import *
import tkinter

import subprocess

from connect_module import ConnectModule
from gcode_module import GcodeModule, GcodeProcessorDialog
from mode_module import ModeModule
from microscope_module import MicroscopeModule
from status_module import StatusModule

#import DoD.main_gui

# Set working directory to root
import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


class MainUI():
    def __init__(self, DoDUI=None):
        self.DoDUI = DoDUI

        self.root = Tk()
        #root.geometry('1600x800')
        self.root.title('Microprinter Host')

        self.frame_top = Frame(self.root)
        self.frame_top.grid(row=1, column=1, sticky='N')


        self.frame_top_left = Frame(self.frame_top)
        self.frame_top_left.grid(row=1, column=1, padx=5, pady=5, sticky='NW')

        self.connect_module = ConnectModule(self.frame_top_left, self)
        self.connect_module.frame.grid(row=1, column=1, sticky='N')

        self.mode_module = ModeModule(self.frame_top_left, self)
        self.mode_module.frame.grid(row=2, column=1, sticky='S')




        self.frame_top_right = Frame(self.frame_top)
        self.frame_top_right.grid(row=1, column=2, padx=5, pady=5, sticky='NE')

        self.gcode_module = GcodeModule(self.frame_top_right, self)
        self.gcode_module.frame.grid(row=1, column=1, sticky='N')



        self.frame_bottom = Frame(self.root)
        self.frame_bottom.grid(row=2, column=1, sticky='SW')

        self.status_module = StatusModule(self.frame_bottom, self)
        self.status_module.frame.grid(row=1, column=1, sticky='W')

        #self.microscope_module = MicroscopeModule(self.frame_bottom, self)
        #self.microscope_module.pack()

        self.status_module.set_status('MicroPrinter Host initialized')

    def main_loop(self):
        self.root.mainloop()




if __name__ == '__main__':
    mainUI = MainUI()
    mainUI.main_loop()
