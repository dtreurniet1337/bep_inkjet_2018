import pyb
import time

pin_min = pyb.Pin('X12', pyb.Pin.IN)
pin_max = pyb.Pin('X11', pyb.Pin.IN)
pin_step = pyb.Pin('Y1', pyb.Pin.OUT_PP)
pin_dir = pyb.Pin('Y2', pyb.Pin.OUT_PP)

pin_ena = pyb.Pin('X8', pyb.Pin.OUT_PP)
pin_ena.value(1)

while True:
    if pin_min.value() == 1: pyb.LED(1).on()
    elif pin_max.value() == 1: pyb.LED(1).on()
    else: pyb.LED(1).off()



    print(str(pin_min.value()) + ' ' + str(pin_max.value()))
