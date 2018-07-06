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
        self.p_NCHG.value(1)
        self.p_LAT.value(1)
        self.p_LAT.value(0)
        self.p_NCHG.value(1)


    def _fire_nozzles(self):
        self.p_NCHG.value(1)
        run_dac(len(self.waveform), addressof(self.waveform))

    def fire(self, B='0', C='0', S='M', Q='E'):
        droplet_size = self._get_size(S)
        droplet_quality = self._get_quality(Q)
        signal = SequenceFactory().get_sequence2(nozzles_black=self._bin_to_range(B),
                                                nozzles_cyan=self._bin_to_range(C),
                                                nozzles_yellow=self._bin_to_range(C),
                                                nozzles_magenta=self._bin_to_range(C),
                                                size=droplet_size,
                                                quality=droplet_quality)
        self._fire(signal)

    def fire_all(self, S='M', Q='E'):
        droplet_size = self._get_size(S)
        droplet_quality = self._get_quality(Q)
        signal = SequenceFactory().get_sequence2(  nozzles_black=range(1, 91),
                                                nozzles_cyan=range(1, 31),
                                                nozzles_yellow=range(1, 31),
                                                nozzles_magenta=range(1, 31),
                                                size=droplet_size,
                                                quality=droplet_quality)
        self._fire(signal)

    def _get_size(self, S):
        if S=='S': return 'small'
        if S=='M': return 'medium'
        if S=='L': return 'large'
        return 'medium'

    def _get_quality(self, Q):
        if Q=='E': return 'economy'
        if Q=='J': return 'jeff'
        if Q=='1': return 'VSD1'
        if Q=='2': return 'VSD2'
        if Q=='3': return 'VSD3'
        if Q=='A': return 'all'
        return 'all'

    def _bin_to_range(self, bin):
        counter = 1
        lst = []
        bin = list(bin)

        for i in bin:
            if i == '1': lst.append(counter)
            counter += 1
        return lst

    def _fire(self, signal):
        for i in range(100):
            self._wake_chip()
            self._latch()
            dma_functions.output_signal(signal)
            self._all_signals_low()
            self._fire_nozzles()
            time.sleep(0.001)

    def _all_signals_low(self):
        self.p_SIBL.value(0)
        self.p_SICL.value(0)
        self.p_CK.value(0)
        self.p_CH.value(0)

    def _wake_chip(self):
        self.p_NCHG.value(1)
        time.sleep(0.0001)
        self.p_NCHG.value(0)
        self.p_LAT.value(1)
        self.p_LAT.value(0)
        for i in range(51):
            self.p_NCHG.value(1)
            time.sleep_us(105)
            self.p_NCHG.value(0)
            time.sleep_us(105)
        self.p_NCHG.value(1)



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

    cmp(r4, 1)
    ble(skip_pulse)

    # Pulse CH pin
    # NCHG Down
    movwt(r2, stm.GPIOB)
    movw(r3, 1<<8)
    strh(r3, [r2, stm.GPIO_BSRRH])
    # CH Up
    movwt(r2, stm.GPIOB)
    movw(r3, 1<<9)
    strh(r3, [r2, stm.GPIO_BSRRL])

    # delay for a bit
    movwt(r7, 20)
    label(delay_on2)
    sub(r7, r7, 1)
    cmp(r7, 0)
    bgt(delay_on2)

    # CH Down
    movw(r3, 1<<9)
    strh(r3, [r2, stm.GPIO_BSRRH])
    label(skip_pulse)
    # NCHG Up
    movwt(r2, stm.GPIOB)
    movw(r3, 1<<8)
    strh(r3, [r2, stm.GPIO_BSRRL])

    mov(r3, r0) # reset counter to waveform length
    mov(r7, r1) # reset waveform address


    # loop 4 times
    sub(r4, r4, 1)
    label(loop_four)
    cmp(r4, 0)
    bgt(loop2)
