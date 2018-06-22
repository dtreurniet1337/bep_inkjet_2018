from tkinter import *
import tkinter



class ModeModule(Frame):
    def __init__(self, root, master):
        self.root = root
        self.master = master
        self.frame = Frame(self.root, relief=RIDGE)

        self.lbl_execute = Label(self.frame, text='Execute')
        self.bt_single = Button(self.frame, text='Single', command=self.single_pressed)
        self.bt_auto = Button(self.frame, text='Auto', command=self.auto_pressed)

        self.lbl_steppers = Label(self.frame, text='Stepper control')
        self.bt_ena_stepper = Button(self.frame, text='Enable', command=self.enable_pressed)
        self.bt_dis_stepper = Button(self.frame, text='Disable', command=self.disable_pressed)


        self.bt_list = [self.bt_single, self.bt_auto, self.bt_ena_stepper, self.bt_dis_stepper]
        self.disable_all()


        self.lbl_execute.grid(row=1, column=1, columnspan=2)
        self.bt_single.grid(row=2, column=1)
        self.bt_auto.grid(row=2, column=2)
        self.lbl_steppers.grid(row=3, column=1, columnspan=2)
        self.bt_ena_stepper.grid(row=4, column=1)
        self.bt_dis_stepper.grid(row=4, column=2)

    def disable_all(self):
        for b in self.bt_list: b['state'] = DISABLED
    def enable_all(self):
        for b in self.bt_list: b['state'] = NORMAL

    def single_pressed(self):
        dialog = SingleDialog(self)

    def auto_pressed(self):
        pass

    def enable_pressed(self):
        r = self.master.connect_module.send_command('G11')

    def disable_pressed(self):
        r = self.master.connect_module.send_command('G10')

    def fire_pressed(self):
        self.master.DoDUI.fire_nozzle()


class SingleDialog():
    def __init__(self, master):
        self.root = Tk()
        self.master = master
        self.frame = Frame(self.root, padx=5, pady=5)

        self.lbl_command = Label(self.frame, text='Command')
        self.ent_command = Entry(self.frame)

        self.bt_send = Button(self.frame, text='Send', command=self.send_pressed)


        self.frame.grid(row=1, column=1)

        self.lbl_command.grid(row=1, column=1, sticky='W')
        self.ent_command.grid(row=1, column=2, sticky='W')

        self.bt_send.grid(row=2, column=1)

        self.root.title('Single command mode')
        self.root.mainloop()



    def send_pressed(self):
        try:
            command = self.ent_command.get().strip()
        except Exception as e:
            print('Invalid entry')
            return
        response = self.master.master.connect_module.send_command(command)
