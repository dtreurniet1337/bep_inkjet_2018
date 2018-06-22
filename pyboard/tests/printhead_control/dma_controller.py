import pyb
import time
import stm
import machine
from array import array
from uctypes import addressof



def output_signal(signal):
    '''
    This function bit-bangs an array of 16-bit words
    to channel GPIOB which is configured as:

    B0 = Y11
    B1 = Y12
    B2 = NC
    B3 = X17
    B4 = P2
    B5 = NC
    B6 = X9
    B7 = X10

    B8  = Y3    * SICL
    B9  = Y4    * SIBL
    B10 = Y9
    B11 = Y10
    B12 = Y5    * CK
    B13 = Y6    * LAT
    B14 = Y7    * CH
    B15 = Y8    * NCHG

    The pins with stars are connected to the printhead as indicated.

    The function expects the address of the array that contains all words
    with the right bits at the right place. The template:
    xxxx00xx00000000

    The signal factory should make sure the input fits the template.

    Example use:

    signal = signal_factory.get_sequence()     <-- this should return a list of words
    dma_controller.output_signal(signal)

    '''
    print("Outputting signal of length %s..."%(len(signal)), end='')
    _output_signal_ass(addressof(array('i', signal)), len(signal))
    print("Done")
    return True

@micropython.asm_thumb
def _output_signal_ass(r0, r1):
    # Inputs:
    # r0 = signal array
    # r1 = signal length


    # r5 = GPIO register
    movwt(r5, stm.GPIOB)

    # Set GPIO speed to ludricrous
    movwt(r4, 0xFFFFFFFF)
    strh(r4, [r5, stm.GPIO_OSPEEDR])

    # r6 = delay counter
    # r7 = bitmask

    ######################### Loop start #############################
    b(loop_entry)
    label(loop1)

    # Load a word of array at address r0 into r7
    ldr(r7, [r0, 0])

    # Set pins by putting the value of r7 into the output register
    strh(r7, [r5, stm.GPIO_ODR])

    # Increment signal address by 4 (for next value)
    add(r0, r0, 4)


    # loop r0 times
    sub(r1, r1, 1)
    label(loop_entry)
    cmp(r1, 0)
    bgt(loop1)
