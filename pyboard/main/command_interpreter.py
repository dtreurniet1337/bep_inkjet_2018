import pyb
from motion_stage_controller import stageController
from printhead_controller import printheadController
import config
import machine

class commandInterpreter():
    def __init__(self, stage_controller, printhead_controller):
        self.stage_controller = stage_controller
        self.printhead_controller = printhead_controller

        self.valid_gcodes = config.VALID_GCODES



    def _get_gcode_components(self, gcode):
        components = gcode.split(' ')
        gcode_dict = {}
        for c in components:
            k = c[0]
            v = c[1:]
            gcode_dict[k] = v
        return gcode_dict


    def _is_gcode(self, command):
        try:
            if command.split(' ')[0][0] == 'G':
                return command.split(' ')[0] in self.valid_gcodes
        except Exception as e:
            return False
        return False


    def execute_command(self, command):
        try:
            if self._is_gcode(command):
                return self.execute_gcode(command)
            elif command in config.VALID_COMMANDS:
                if command == 'RESET': machine.reset()
            elif command == 'P1':
                return self.__P1()
            return 'Invalid command: '+str(command)
        except Exception as e:
            return 'execute_command() failed: '+str(e)


    def execute_gcode(self, gcode):

        function_dict = {'0':self._G1,
                         '1':self._G1,
                         '10': self._G10,
                         '11': self._G11,
                         '28': self._G28,
                         '92': self._G92}

        gcode_dict = self._get_gcode_components(gcode)

        try: return function_dict[gcode_dict['G']](gcode_dict)
        except Exception as e: return 'execute_gcode() failed: '+str(e)

        return 'execute_gcode() failed: something went really wrong'


    def _G1(self, gcode_dict):
        if 'X' not in gcode_dict: return 'Missing X coordinate in Gcode'
        if 'Y' not in gcode_dict: return 'Missing Y coordinate in Gcode'
        self.stage_controller.move_to_position((float(gcode_dict['X']), float(gcode_dict['Y'])))
        return 'Moved stage to ['+gcode_dict['X']+', '+gcode_dict['Y']+']'

    def _G10(self, gcode_dict):
        self.stage_controller.enable_stages(False)
        return 'Disabled steppers'

    def _G11(self, gcode_dict):
        self.stage_controller.enable_stages(True)
        return 'Enabled steppers'

    def _G28(self, gcode_dict):
        self.stage_controller.home_stages()
        return 'Homed stage'

    def _G92(self, gcode_dict):
        if 'X' not in gcode_dict: gcode_dict['X'] = 0
        if 'Y' not in gcode_dict: gcode_dict['Y'] = 0
        self.stage_controller.set_position(gcode_dict['X'], gcode_dict['Y'])
        return 'Position set'

    def __P1(self):
        self.printhead_controller.fire(B=10, C=0, S='M', Q='A')
        return 'Fired nozzles'
