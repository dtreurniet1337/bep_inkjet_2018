from tkinter import *
import tkinter
import os

class StatusModule():
    def __init__(self, root, master):
        print(os.getcwd())
        self.root = root
        self.master = master
        self.frame = Frame(self.root)

        self.green_light = PhotoImage(file='img/status_green.png')
        self.yellow_light = PhotoImage(file='img/status_yellow.png')
        self.red_light = PhotoImage(file='img/status_red.png')


        self.status_light = Label(self.frame, image=self.red_light)

        self.status_bar = Label(self.frame)
        self.log_file = 'log.txt'
        self.log = open(self.log_file, 'w')
        self.log.close()

        self.status_light.grid(row=1, column=1, padx=10)
        self.status_bar.grid(row=1, column=2)


    def set_status_light(self, color):
        if color == 'green': self.status_light['image'] = self.green_light
        if color == 'yellow': self.status_light['image'] = self.yellow_light
        if color == 'red': self.status_light['image'] = self.red_light

    def set_status(self, txt):
        self.status_bar['text'] = txt
        self.status_bar.grid(row=1, column=2)

    def log_file(self, txt):
        self.set_status(txt)
        self.master.root.update_idletasks()
        try:
            self.log = open(self.log_file, 'a')
            self.log.write(txt+'\n')
            self.log.close()
        except Exception:
            pass
