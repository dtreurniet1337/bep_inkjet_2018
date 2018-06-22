# def p_raster_nxm(**kwargs):
#     nozzlelist = createnozzlelist(nozzles, m, dy, fan)
#     raster = b''

#     x += verschil
#     print("x aangepast")

#     for k in range(n):
#         raster += (ESC_dollar(hor, (x + dx * k)) + ESC_i_nrs(nozzlelist, color, size)) * rep
#     rasterdata = ESC_v(pmgmt, y) + raster + b'\x0c'
#     return rasterdata

# p_raster_nxm()

# def test_loop(**kwargs):
#     for k in range(n):
#         print(str(k) + ' ' + str(verschil))

# n=5
# verschil = 3
# print('sexy2')
# test_loop()

# dx=250.0
# d_dot=40.0
# x_overlap=0.07*d_dot
# n=dx/x_overlap
# # print('n is ' + str(n) + '\n x_overlap is ' + str(x_overlap))
# n = round(n)
# x_overlap= dx / n
# # print('n round is ' + str(n) + '\n x_overlap is ' + str(x_overlap))

    
# # ESC_v test in printTUPME WERKT beweegt het papier een beetje naar voren
# ddy=y/20
# dddy=y+ddy
# rasterdata = ESC_v(pmgmt, y) + rasterdata1 + ESC_v(pmgmt, dddy) + rasterdata2 + b'\x0c'

# oxn=89
# for k in range(oxn): # k from 0 to value oxn - 1
#     print k

# import serial.tools.list_ports
# ports = list(serial.tools.list_ports.comports())
# for p in ports:
#     print (p)

# x1=1
# y1=1

# x2=9
# y2=2

# a=(y2-y1)/(x2-x1) #coefficient
# print("a: " + str(a))
# b=y1-x1*a
# print("b: " + str(b))

# from tkinter import *

# master = Tk()

# w = Canvas(master, width=600, height=300)
# w.pack()

# w.create_line(5, 40, 200, 100)
# w.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))

# w.create_rectangle(50, 25, 150, 75, fill="blue")

# i = w.create_line(50,100,200,300, fill="red")

# w.coords(i, 50,100,200,250,50,200,100,250) # change coordinates
# w.coords
# w.itemconfig(i, fill="blue") # change color

# w.delete(i) # remove

# w.delete(ALL) # remove all items

# mainloop()

# for k in range(2): # k from 0 to value oxn - 1
#     k1="one"
#     k2="two"
#     k_output=""
#     if k==0:
#         print k
#     if k==1:
#         print "sexy"

### IMPORT ###
from tkinter import *
import serial
from time import sleep
import math

def line_diag ():
    global n_y_steps_round, xlist, ylist, xylist
    global x, y, x1, y1, x2, y2, Dx, Dy
    global d_overlap #use it for single step of stepper

    print("start line_diag")

    ### coefficients ### which units are they in?
    # manual
    x1=0
    y1=0

    x2=400
    y2=250

    # #terminal
    # x1 = int(input("Please enter x1 \n"))
    # y1 = int(input("Please enter y1 \n"))

    # x2 = int(input("Please enter x2 \n"))
    # y2 = int(input("Please enter y2 \n"))

    Dy=y2-y1 #total difference y
    #print(str(Dy))
    Dx=x2-x1 #total difference x



    ### droplet size ###
    d=60 #micron
    d_overlap = 0.5*d

    ### calculations ### #use python3!
    a=(Dy)/(Dx) #coefficient
    #print("a: " + str(a))
    b=y1-x1*a
    #print("b: " + str(b))

    #vertical lines
    n_y_steps=Dy/d_overlap #number ofsteps arduino takes to overlap dots # Abel this only works for vertical lines, otherwise overlap wont be as good
    #print(str(n_y_steps))
    n_y_steps_round=int(n_y_steps) #make integer
    print("Times stepper will move: " + str(n_y_steps_round))
    y_start=y1

    # Diagonal lines
    lineLength = math.sqrt(Dx**2 + Dy**2)
    n_steps = lineLength / d_overlap
    n_steps_round = math.ceil(n_steps)
    # Vertical step size
    d_overlap_y = Dy / lineLength * d_overlap
    # Horizontal step size
    d_overlap_x = Dx / lineLength * d_overlap

    ### Usage ###
    #y=ax+b -> x=(y-b)/a
    xlist = []
    ylist = []
    for k in range(n_steps_round+1):
        y= k*d_overlap_y + y1
        ylist.insert(k,y)

        x = (y-b) / a # Possible to use different functions for different lines
        xlist.insert(k,x)

    print( xlist)

    xylist = [xlist, ylist] # to get fifth y value call xylist[1][4]

    # for x,y in zip(xlist,ylist):
    #     print("(x,y): (" + str(x) + "," + str(y) + ")")
    print("end line_diag")
line_diag()

def arduino_init():
    global operatingSystem
    global linuxpath
    global time
    print("start arduino_init()")
    # Path arduino
    linuxpath0="/dev/ttyUSB0"
    linuxpath1="/dev/ttyUSB1"
    linuxpath2="/dev/ttyACM0"
    linuxpath3="/dev/ttyACM1"
    linuxpath=linuxpath0
    # test which path is available ABEL

    operatingSystem=1
    d_overlap_k=0
    time=2
#arduino_init()

def sendtoArduino():
    print("sendtoArduino")
    print("sleepTime1")
    sleepTime(time, "stepping")
    #calculate()
    #global dy_microns
    #dy_microns=d_overlap

    if operatingSystem == 1:
        arduino = serial.Serial(linuxpath)
    elif operatingSystem == 2:
        arduino = serial.Serial('COM3')
    else:
        print("Select operationSystem")
    
    print(arduino.name)
    #arduino = serial.Serial('COM3') #COM3 is the usb port from the arduino, may vary
    #timeout=0.1 #arduino connectie maken
    if arduino.is_open == 1:                    
        print("usb working")   # no conflict on usb
    
    # ?start = arduino.readline().decode().strip()
    # ?print(start)
    
    translationRate = 500 #one rotation is 500 microns rotation using the 28BYJ-48 stepper motor
    #stepsperRotation = 64*64 #one rotation is 64*64=4096 steps using the 28BYJ-48 stepper motor
    stepsperRotation = 200*16 #one rotation is 200*16=3200 steps using the NEMA-17 stepper motor
    #steps = dy_microns.get()/translationRate*stepsperRotation
    #steps = d_overlap_k/translationRate*stepsperRotation
    #steps = 5/translationRate*stepsperRotation
    steps = input("How many steps to move? \n")
    distanceStr = str(steps)
    print ("steps to travel")
    print (steps)
    
    
    arduino.write(distanceStr.encode()) #newpos is the variable distance to travel
    print("sleepTime2")
    sleepTime(time, "stepping")
    arduino.close()  
    print ("usb closed, program finished")

def tkinter_show_line():
    ### tkinter ###

    master = Tk()

    w = Canvas(master, width=Dx, height=Dy)
    w.pack()

    w.create_line(x1-x1, y1-y1, x2-x1, y2-y1)

    for x,y in zip(xlist,ylist):
        w.create_line(x-x1-5,y-y1,x-x1+5,y-y1, fill="red") # to check if dots are placed right


    mainloop()
# tkinter_show_line()

def arduinoLoop():
    global d_overlap_k
    for k in range(len(ylist)):
        d_overlap_k=ylist[k]
        print("d_overlap_k: " + str(d_overlap_k))
        sendtoArduino()

def sleepTime(time, text):
    print("Start, now wait " + str(time) + " seconds for " + text + ".")
    sleep(time)
    print("End of " + text + ".")

print("End of line functions setup")

def print_esc_commands(event=None, PLNAME='def'):
    global n_y_steps
    
    for n_y_steps in range(n_y_steps_round):
        print (n_y_steps)

        if PLNAME == 'def':
            plname = lpname_var.get()
        else:
            plname = simpledialog.askstring("Set Printer Name", "Linux printer name:", initialvalue=lpname_var.get())
            lpname_var.set(plname)
        # linux_command = "lp -d "+printersParDict[printerSelected]['linux-name']+" -oraw "+path
        save_temp()
        try:
            subprocess.call(["lp", "-d", plname, "-oraw", path])
        except:
            tk.messagebox.showerror("Linux Error", "Could not print the data due to a error in Linux, the printername is probably not setup correctly.")

#sendtoArduino()
#print_esc_commands()
#sleepTime(2, "waiting")

