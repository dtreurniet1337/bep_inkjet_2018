import pyb
import time

end1 = pyb.Pin('X3', pyb.Pin.IN)
end2 = pyb.Pin('X4', pyb.Pin.IN)
end3 = pyb.Pin('X12', pyb.Pin.IN)
end4 = pyb.Pin('X11', pyb.Pin.IN)

while True:
    print(str(end1.value())+' '+str(end2.value())+' '+str(end3.value())+' '+str(end4.value())+' \n')
    time.sleep(0.01)
