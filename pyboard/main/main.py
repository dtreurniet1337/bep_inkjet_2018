import config

from motion_stage_controller import stageController
from printhead_controller import printheadController
from serial_controller import serialListener
from command_interpreter import commandInterpreter

import time
import pyb



class mainController():
    """
    Main print machine controller
    """

    def __init__(self):
        self.stage_controller = stageController()
        self.printhead_controller = printheadController()
        self.serial = serialListener()
        self.commander = commandInterpreter(self.stage_controller, self.printhead_controller)

        print('finished main_controler initialization')


    def main_loop(self):
        print('entering main_loop')
        while True:
            command = self.serial.get_message()

            # turn on Led 2 when processing a command
            if command:
                pyb.LED(2).on()
                f = self.commander.execute_command(command)
                pyb.LED(2).off()
                self.serial.send_message(f)

            if self.stage_controller.is_enabled(): pyb.LED(3).on()
            else: pyb.LED(3).off()







if __name__ == '__main__':
    main_controller = mainController()
    main_controller.main_loop()
