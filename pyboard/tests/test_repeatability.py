import pyb
import time

p_step = pyb.Pin('X2', pyb.Pin.OUT_PP)
p_dir = pyb.Pin('X1', pyb.Pin.OUT_PP)
p_ena = pyb.Pin('X8', pyb.Pin.OUT_PP)

reps = 5
steps = 2
delay = 500


def step(steps):
    for s in range(steps):
        p_step.value(1)
        time.sleep_us(1)
        p_step.value(0)
        time.sleep_us(delay)

p_ena.value(0)
for i in range(reps):
    p_dir.value(0)
    for j in range(5):
        step(steps)
        time.sleep(1)

    p_dir.value(1)
    for j in range(5):
        step(steps)
        time.sleep(1)





p_ena.value(1)
