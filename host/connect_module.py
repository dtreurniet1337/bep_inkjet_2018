from tkinter import *
import tkinter
import sys
import glob
import serial
import random
import time
import subprocess


class ConnectModule():
    def __init__(self, root, master, test_entries=False):
        self.root = root
        self.master = master
        self.frame = Frame(self.root, relief=GROOVE, border=1)

        self.ser = serial.Serial()
        self.test_entries = test_entries

        self.update_bt = Button(self.frame, command=self.update_pressed, text='Refresh')

        self.lb = Listbox(self.frame, selectmode=SINGLE)
        self.update_ports()

        self.connect_bt = Button(self.frame, command=self.connect_pressed, text='Connect')
        self.disconnect_bt = Button(self.frame, command=self.disconnect_pressed, text='Disconnect', state=DISABLED)

        self.is_connected = False


        self.update_bt.grid(row=1, column=1, columnspan=2)
        self.lb.grid(row=2, column=1, columnspan=2)
        self.connect_bt.grid(row=3, column=1)
        self.disconnect_bt.grid(row=3, column=2)

    def update_pressed(self):
        self.update_ports()

    def connect_pressed(self):
        if not self.lb.curselection(): return
        self.ser.port = self.lb.get(self.lb.curselection()[0])
        try:
            self.ser.open()
        except Exception as e:
            print('Connection failed: %s'%(e))
            return

        self.is_connected = True
        self.connect_bt['state'] = DISABLED
        self.disconnect_bt['state'] = NORMAL
        self.master.mode_module.enable_all()
        self.master.status_module.set_status('Connected to %s'%(self.ser.port))
        self.master.status_module.set_status_light('green')

    def disconnect(self):
        self.disconnect_pressed()

    def disconnect_pressed(self):
        try:
            self.ser.close()
        except Exception as e:
            print('Disconnect failed: %s'%(e))
            return

        self.is_connected = False
        self.disconnect_bt['state'] = DISABLED
        self.connect_bt['state'] = NORMAL
        self.master.mode_module.disable_all()
        self.master.status_module.set_status('Disconnected from %s'%(self.ser.port))
        self.master.status_module.set_status_light('red')

    def get_response(self):
        if self.is_connected:
                data = self.ser.readline()
                if data != None: return data.decode('ascii')
                return None
        return 'Error: not connected'

    def send_command(self, command, response=True):
        if not self.is_connected: return 'Error: not connected'
        self.ser.write(command.encode('ascii'))
        if response:
            while True:
                r = self.get_response()
                if r != None: return r
        return True

    def print_file(self, file):
        if not self.is_connected: return 'Error: not connected'
        try:
            f = open(file, 'r')
            lines = f.readlines()
            f.close()
        except Exception as e:
            return 'Error: '+str(e)

        # Purge
        subprocess.call(["lp", "-d", '235', "-oraw", 'prn/temp.prn'])
        time.sleep(1)

        for l in lines:
            if l.strip() == '': continue
            if l.strip()[:2] == 'P1': continue
            if l.strip()[:3] == 'G28':
                print('Skipping homing')
                continue

            print('Sending: %s'%(l.strip()))
            self.ser.write(l.strip().encode('ascii'))
            while True:
                r = self.get_response()
                if r != None:
                    self.master.status_module.set_status(r.strip())
                    self.master.root.update_idletasks()
                    break
            time.sleep(0.22)
        self.master.status_module.set_status('Finished printing '+str(file))
        self.master.status_module.set_status_light('green')
        self.master.root.update_idletasks()

    def update_ports(self):
        available_ports = self.serial_ports()
        self.lb.delete(0, self.lb.size())
        for i, port in enumerate(available_ports):
            self.lb.insert(i, port)
        if self.test_entries:
            for i in range(10):
                self.lb.insert(i, 'test entry '+str(random.random()))

    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
