from pyb import Pin, LED, Timer
import config
import time
import math
import micropython
micropython.alloc_emergency_exception_buf(100)

class stageController():
    def __init__(self):
        # Define motion stages
        self.x_stage = stage('x',
                             config.X_STEP,
                             config.X_DIR,
                             config.X_END_MAX,
                             config.X_END_MIN)
        self.y_stage = stage('y',
                              config.Y_STEP,
                              config.Y_DIR,
                              config.Y_END_MAX,
                              config.Y_END_MIN)

        # Define enable pin and disable steppers
        self.stage_ena = Pin(config.STEP_ENA, Pin.OUT_PP)
        self.stage_ena.value(1)

        # Define other properties
        self.range = config.STAGE_RANGE

        # Init position at 0,0 and set homed to False
        self.position = [0, 0]
        self.homed = False

        print('stage controller initialized')


    def move_to_position(self, position):
        # Check if target position is within stage range
        if position[0] < 0 or position[0] > self.range[0]:
            return 'target out of range'
        if position[1] < 0 or position[1] > self.range[1]:
            return 'target out of range'

        # Move
        self._move_square(position)

    def enable_stages(self, bool):
        if bool: self.stage_ena.value(0)
        else: self.stage_ena.value(1)

    def is_enabled(self):
        return not self.stage_ena.value()

    def home_stages(self):
        self.enable_stages(True)

        self.x_stage.move_end(config.X_HOME_DIR)
        time.sleep(0.5)
        self.x_stage.move_delta(0.1, not config.X_HOME_DIR)
        time.sleep(0.5)
        self.x_stage.move_end(config.X_HOME_DIR, accel=False)

        self.y_stage.move_end(config.Y_HOME_DIR)
        time.sleep(0.5)
        self.y_stage.move_delta(0.1, not config.Y_HOME_DIR)
        time.sleep(0.5)
        self.y_stage.move_end(config.Y_HOME_DIR, accel=False)

        self.position = [0, 0]


    def _move_square(self, position):
        # Calculate distance to move
        delta_x = position[0] - self.position[0]
        delta_y = position[1] - self.position[1]

        # Determine directions
        if position[0] < self.position[0]: x_dir = 0
        else: x_dir = 1
        if position[1] < self.position[1]: y_dir = 0
        else: y_dir = 1

        # Enable steppers
        self.enable_stages(True)

        # Execute move
        self.x_stage.move_delta(abs(delta_x), x_dir)
        self.y_stage.move_delta(abs(delta_y), y_dir)

        self.position = position

    def set_position(self, x, y):
        self.position = [x, y]
        return True




class stage():
    def __init__(self, name, p_step, p_dir, p_max, p_min):
        self.name = name

        self.p_step = Pin(p_step, Pin.OUT_PP)
        self.p_dir = Pin(p_dir, Pin.OUT_PP)
        self.p_max = Pin(p_max, Pin.IN)
        self.p_min = Pin(p_min, Pin.IN)

        self.ms = config.STAGE_MICROSTEPPING
        self.pitch = config.STAGE_PITCH
        self.mm_per_step = float(self.pitch) / float(self.ms*config.STAGE_STEPS_PER_REV)

        print('stage %s initialized'%(self.name))

    # Functions for checking whether endswitch is triggered
    def at_min(self): return self.p_min.value()
    def at_max(self): return self.p_max.value()

    def move_end(self, dir):
        self.p_dir.value(dir)

        while True:
            if dir == 1 and self.p_min.value() == 1: break
            if dir == 0 and self.p_max.value() == 1: break

            self.p_step.value(1)
            time.sleep_us(200)
            self.p_step.value(0)
            time.sleep_us(200)



    def move_delta(self, delta, dir):
        self.p_dir.value(dir)
        n_steps = int(delta / self.mm_per_step)
        for i in range(n_steps):
            self.p_step.value(1)
            time.sleep_us(200)
            self.p_step.value(0)
            time.sleep_us(200)
