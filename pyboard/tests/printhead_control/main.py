from sequence_factory import SequenceFactory
import dma_controller
import time
import config
from pyb import Pin
import pyb


p_SICL = Pin(config.SICL, Pin.OUT_PP)
p_SIBL = Pin(config.SIBL, Pin.OUT_PP)
p_CK = Pin(config.CK, Pin.OUT_PP)
p_LAT = Pin(config.LAT, Pin.OUT_PP)
p_CH = Pin(config.CH, Pin.OUT_PP)
p_NCHG = Pin(config.NCHG, Pin.OUT_PP)

p_LAT.value(0)
p_NCHG.value(0)

dac = pyb.DAC(1)

def latch_data():
    p_LAT.value(1)
    p_LAT.value(0)

def fire():
    p_NCHG.value(1)
    output_waveform()
    p_NCHG.value(0)

def output_waveform():
    dac.write_timed(waveform_buf, freq=4000000, mode=pyb.DAC.CIRCULAR)


signal = SequenceFactory().get_sequence(    nozzles_black=[1,4,6,8,12,16,28,32],
                                            nozzles_cyan=[1,5,7,12],
                                            nozzles_yellow=[3,6,9],
                                            nozzles_magenta=[5,8,12,10],
                                            quality='VSD2',
                                            size='medium')

waveform = [725,125,125,975,975,725,725,125,125,975,975,725,725,125,125,975,975,725,725,50,50,500,500,1000,1000,725,725,325,325,725,725,125,125,975,975,725,725,125,125,975,975,725,725,125,125,975,975,725,725,50,50,500,500,1000,1000,725]
#waveform = [500,475,450,425,400,375,350,325,300,275,250,225,200,175,150,125,100,75,50,25,0,0,0,0,0,0,0,0,125,250,375,500,625,750,875,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,975,950,925,900,875,850,825,800,775,750,725,700,675,650,625,600,575,550,525,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500,500]

waveform_buf = bytearray(len(waveform))
for i in range(len(waveform)):
    waveform_buf[i] = int(255*(waveform[i]/1000))


print('Signal:')
print(signal)
print('Firing in\n3...')
time.sleep(1)
print('2...')
time.sleep(1)
print('1...')
time.sleep(1)

dma_controller.output_signal(signal)
latch_data()
fire()
time.sleep(1)
