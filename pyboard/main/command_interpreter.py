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
            if command.split(' ')[0][0] == 'G' or command.split(' ')[0][0] == 'P':
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
            return 'Invalid command: '+str(command)
        except Exception as e:
            return 'execute_command() failed: '+str(e)


    def execute_gcode(self, gcode):

        function_dict = {'G0':self._G1,
                         'G1':self._G1,
                         'G10': self._G10,
                         'G11': self._G11,
                         'G28': self._G28,
                         'G92': self._G92,
                         'P1': self._P1,
                         'P2': self._P2}

        gcode_dict = self._get_gcode_components(gcode)

        try: return function_dict[gcode.split(' ')[0]](gcode_dict)
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

    def _P1(self, gcode_dict):
        if 'B' not in gcode_dict: gcode_dict['B'] = '0'
        if 'C' not in gcode_dict: gcode_dict['C'] = '0'
        if 'S' not in gcode_dict: gcode_dict['S'] = 'M'
        if 'Q' not in gcode_dict: gcode_dict['Q'] = 'E'
        self.printhead_controller.fire(B=str(gcode_dict['B']), C=str(gcode_dict['C']), S=str(gcode_dict['S']), Q=str(gcode_dict['Q']))
        return 'Fired black: '+str(gcode_dict['B'])+' color: '+str(gcode_dict['C'])+' size: '+str(gcode_dict['S'])+' quality: '+str(gcode_dict['Q'])

    def _P2(self, gcode_dict):
        if 'S' not in gcode_dict: gcode_dict['S'] = 'M'
        if 'Q' not in gcode_dict: gcode_dict['Q'] = 'E'
        self.printhead_controller.fire_all(S=str(gcode_dict['S']), Q=str(gcode_dict['Q']))
        return 'Fired all nozzles'
