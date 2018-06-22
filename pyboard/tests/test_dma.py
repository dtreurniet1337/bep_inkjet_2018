import pyb
import time
import stm
import machine
from array import array
from uctypes import addressof


@micropython.asm_thumb
def output_signal(r0, r1):
    # r0 = signal array
    # r1 = signal length


    # r5 = GPIO register
    movwt(r5, stm.GPIOA)
    movwt(r4, 0x0000)
    strh(r4, [r5, stm.GPIO_OSPEEDR])
    # r6 = delay counter
    # r7 = bitmask

    ######################### Loop start #############################
    b(loop_entry)
    label(loop1)

    # Load signal byte in r7
    ldr(r7, [r0, 0])

    # set LEDs by putting the value of r7 into
    strh(r7, [r5, stm.GPIO_ODR])

    # Increment signal address by 4 (for next value)
    add(r0, r0, 4)


    # loop r0 times
    sub(r1, r1, 1)
    label(loop_entry)
    cmp(r1, 0)
    bgt(loop1)


@micropython.asm_thumb
def flash_led(r0):
    # get the GPIOA address in r1
    movwt(r1, stm.GPIOA)

    # get the bit mask for PA14 (the pin LED #2 is on)
    movw(r2, 1 << 13)

    b(loop_entry)

    label(loop1)

    # turn LED on
    strh(r2, [r1, stm.GPIO_BSRRL])

    # turn LED off
    strh(r2, [r1, stm.GPIO_BSRRH])

    # loop r0 times
    sub(r0, r0, 1)
    label(loop_entry)
    cmp(r0, 0)
    bgt(loop1)

#signal = [0,1<<13,1<<13,1<<13,1<<13]*1000
#signal.append(0)
#array_signal = array('i', signal)
#output_signal(addressof(array_signal), len(signal))

p = pyb.Pin('X1') # X1 has TIM2, CH1
tim = pyb.Timer(2, freq=12000000)
ch = tim.channel(1, pyb.Timer.PWM, pin=p)
ch.pulse_width_percent(50)

while True:
    pass
