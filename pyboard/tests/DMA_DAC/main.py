import stm
import pyb
from array import array
from uctypes import addressof

pin = pyb.Pin('Y7', pyb.Pin.OUT_PP)
waveform = [500,475,450,425,400,375,350,325,300,275,250,225,200,175,150,125,100,75,50,25,0,0,0,0,0,0,0,0,125,250,375,500,625,750,875,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,975,950,925,900,875,850,825,800,775,750,725,700,675,650,625,600,575,550,525,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500]

factor = max(waveform)
for i in range(len(waveform)):
    waveform[i] = int((waveform[i]/factor)*255)

def init_dac():
    dac = pyb.DAC(1)
    init_dac_assy()

@micropython.asm_thumb
def init_dac_assy():
    movwt(r5, stm.DAC)

    # DAC EN1
    movwt(r6, 0x00001001)
    str(r6, [r5, stm.DAC_CR])

@micropython.asm_thumb
def run_dac(r0, r1):
    # r0 = length of waveform array
    # r1 = address of waveform array
    # r2 = delay counter
    # r3 = waveform length save
    # r4 = pulse counter
    # r5 = DAC base addressof
    # r6 = waveform value holder
    # r7 = waveform index counter

    movwt(r5, stm.DAC) # store DAC base address in r5
    mov(r3, r0) # set counter to waveform length
    mov(r7, r1) # save address of waveform
    mov(r4, 4) # number of pulses to give

    b(loop_four)
    label(loop2)

    b(loop_entry)
    label(loop1)

    ldrb(r6, [r7, 0]) # get the value of waveform array
    strh(r6, [r5, stm.DAC_DHR8R1]) # set DAC output
    add(r7, r7, 4) # increment to select next waveform value

    # delay for a bit
    movwt(r2, 3)
    label(delay_on)
    sub(r2, r2, 1)
    cmp(r2, 0)
    bgt(delay_on)


    # loop through waveform
    sub(r3, r3, 1)
    label(loop_entry)
    cmp(r3, 0)
    bgt(loop1)

    # Pulse CH pin
    movwt(r2, stm.GPIOB)
    movw(r3, 1<<14)
    strh(r3, [r2, stm.GPIO_BSRRL])

    # delay for a bit
    movwt(r7, 2)
    label(delay_on2)
    sub(r7, r7, 1)
    cmp(r7, 0)
    bgt(delay_on2)

    strh(r3, [r2, stm.GPIO_BSRRH])

    mov(r3, r0) # reset counter to waveform length
    mov(r7, r1) # reset waveform address


    # loop 4 times
    sub(r4, r4, 1)
    label(loop_four)
    cmp(r4, 0)
    bgt(loop2)



init_dac()
while True:
    pyb.LED(2).toggle()
    pyb.DAC(1).write(127)
    run_dac(len(waveform), addressof(array('i', waveform)))
    pyb.DAC(1).write(127)
