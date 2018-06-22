import config
import dma_functions
from sequence_factory import SequenceFactory
from pyb import Pin, DAC
import time
from array import array
from uctypes import addressof



class printheadController():
    def __init__(self):
        self.p_SICL = Pin(config.SICL, Pin.OUT_PP)
        self.p_SIBL = Pin(config.SIBL, Pin.OUT_PP)
        self.p_CK = Pin(config.CK, Pin.OUT_PP)
        self.p_LAT = Pin(config.LAT, Pin.OUT_PP)
        self.p_CH = Pin(config.CH, Pin.OUT_PP)
        self.p_NCHG = Pin(config.NCHG, Pin.OUT_PP)

        self.p_LAT.value(0)
        self.p_NCHG.value(0)

        self.dac = DAC(1)
        self.dac.write(127)

        waveform = config.WAVEFORM
        factor = max(waveform)
        for i in range(len(waveform)):
            waveform[i] = int(255*(waveform[i]/factor))
        self.waveform = array('i', waveform)

    def _latch(self):
        self.p_LAT.value(1)
        self.p_LAT.value(0)

    def _fire_nozzles(self):
        self.p_NCHG.value(1)
        run_dac(len(self.waveform), addressof(self.waveform))
        self.p_NCHG.value(0)


    def fire_n_nozzles(self, n):
        signal = SequenceFactory().get_sequence(nozzles_black=range(1,n),
                                                size='medium',
                                                quality='economy')
        for i in range(1000):
            self._latch()
            dma_functions.output_signal(signal)
            self._latch()
            self._fire_nozzles()


    def fire(self, B=0, C=0, S='M', Q='E', F=4000000):
        if S=='S': droplet_size = 'small'
        if S=='M': droplet_size = 'medium'
        if S=='L': droplet_size = 'large'

        if Q=='E': droplet_quality = 'economy'
        if Q=='J': droplet_quality = 'jeff'
        if Q=='1': droplet_quality = 'VSD1'
        if Q=='2': droplet_quality = 'VSD2'
        if Q=='3': droplet_quality = 'VSD3'
        if Q=='A': droplet_quality = 'all'

        signal = SequenceFactory().get_sequence(nozzles_black=range(1,B+1),
                                                nozzles_cyan=range(1,C+1),
                                                nozzles_yellow=range(1,C+1),
                                                nozzles_magenta=range(1,C+1),
                                                size=droplet_size,
                                                quality=droplet_quality)
        #for i in range(1000):
        self._latch()
        dma_functions.output_signal(signal)
        self._latch()
        self._fire_nozzles()
        time.sleep(0.001)



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
    # used to be 3
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

    cmp(r4, 1)
    ble(skip_pulse)

    # Pulse CH pin
    movwt(r2, stm.GPIOB)
    movw(r3, 1<<9)
    strh(r3, [r2, stm.GPIO_BSRRL])

    # delay for a bit
    movwt(r7, 20)
    label(delay_on2)
    sub(r7, r7, 1)
    cmp(r7, 0)
    bgt(delay_on2)

    movw(r3, 1<<9)
    strh(r3, [r2, stm.GPIO_BSRRH])
    label(skip_pulse)

    mov(r3, r0) # reset counter to waveform length
    mov(r7, r1) # reset waveform address


    # loop 4 times
    sub(r4, r4, 1)
    label(loop_four)
    cmp(r4, 0)
    bgt(loop2)
