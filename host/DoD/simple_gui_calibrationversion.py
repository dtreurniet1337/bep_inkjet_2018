#!/usr/bin/python3

"""
Micro positioning tool for printing dropplets using the EPSON xp235 positioning platform

BEP PME 06 Hacking a commercial inkjet printer

Author:     R. Slingerland
Date:       XX-06-2017
Version:    0.1

"""

# ---- Import modules ----
from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from os import *
import os
import serial
import sys
#from main import *

#create the window
root = Tk()

#Operating system
#Linux = 1
#Windows = 2
#Enables zoom function and arduino settings
operatingSystem = 1


# ---- variables ----
#imagePath = "substrate.png"
imagePath = StringVar()

imagePath.set("merged_14.jpg")


#imagePath = filedialog.askopenfilename(title='open')
imageMagnification = 1/4 #default 1/5, change when using a different camera

calibrationLength_x = IntVar()
calibrationLength_y = IntVar()
calibrationLength_x.set(5000) #length of the calibration line in horizontal direction, unit = microns
calibrationLength_y.set(5000) #length of the calibration line in vertical direction, unit = microns

canvasxPosition = 0
canvasyPosition = 0
canvasHeight = 780
canvasWidth = 1040

canvas_abs_x = canvasxPosition+canvasWidth
canvas_abs_y = canvasyPosition+canvasHeight

x0 = IntVar()
y0 = IntVar()
x0.set(0)
y0.set(0)

x1 = IntVar()
y1 = IntVar()
x1.set(0)
y1.set(0)

dx = IntVar()
dy = IntVar()
dx.set(0)
dy.set(0)

x_calix1 = IntVar()
x_calix2 = IntVar()
x_caliy1 = IntVar()
x_caliy2 = IntVar()
x_calix1.set(0)
x_calix2.set(0)
x_caliy1.set(0)
x_caliy2.set(0)

y_calix1 = IntVar()
y_calix2 = IntVar()
y_caliy1 = IntVar()
y_caliy2 = IntVar()
y_calix1.set(0)
y_calix2.set(0)
y_caliy1.set(0)
y_caliy2.set(0)

dx_calix = IntVar()
dy_calix = IntVar()
dx_caliy = IntVar()
dy_caliy = IntVar()
dx_calix.set(0)
dy_calix.set(0)
dx_caliy.set(0)
dy_caliy.set(0)

dx_microns = DoubleVar()
dy_microns = DoubleVar()
dx_microns.set(0)
dy_microns.set(0)

dx_microns_round = DoubleVar()
dy_microns_round = DoubleVar()
dx_microns_round.set(0)
dy_microns_round.set(0)

moveMicrons = DoubleVar()
moveMicrons.set(100)

t = 1 #printcoord variable
#buttonPressed = 1

#modify root window
root.title("Microdroplet positioning tool")
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

#Labels lay-out
headerfont = ('times', 15, 'bold')

def openFilename():
    filename = filedialog.askopenfilename(title='open')
    return filename

#Does not work as wanted, check later
def openImage():
    global imagePath
    global image
    global im
    global im_width
    global photo
    global canvas
    imagePath.set(openFilename())
    print(imagePath.get())
    canvas.destroy()  
    canvas = Canvas(root,height=canvasHeight,width=canvasWidth,xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
    canvas.place(x=canvasxPosition,y=canvasyPosition)
    im = Image.open(imagePath.get())
    im_width, im_height = im.size
    im = im.resize((int(im_width*imageMagnification), int(im_height*imageMagnification)),Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(im)
    image = canvas.create_image(0,0, anchor=NW, image=photo)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    canvas.config(scrollregion=canvas.bbox(ALL))

    
    

# ---- canvas ----

#creating scrollbars
xscrollbar = Scrollbar(root, orient=HORIZONTAL)
xscrollbar.grid(row=1, column=0, sticky=E+W)
yscrollbar = Scrollbar(root)
yscrollbar.grid(row=0, column=1, sticky=N+S)

#creating canvas
canvas = Canvas(root,height=canvasHeight,width=canvasWidth,xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
canvas.place(x=canvasxPosition,y=canvasyPosition)
im = Image.open(imagePath.get())
im_width, im_height = im.size
im = im.resize((int(im_width*imageMagnification), int(im_height*imageMagnification)),Image.ANTIALIAS)
photo = ImageTk.PhotoImage(im)
image = canvas.create_image(0,0, anchor=NW, image=photo)
canvas.grid(row=0, column=0, sticky=N+S+E+W)
canvas.config(scrollregion=canvas.bbox(ALL))

xscrollbar.config(command=canvas.xview)
yscrollbar.config(command=canvas.yview)

# ---- imported ----
zoomcycle = 0
zimg_id = None

if operatingSystem ==2:
    def zoomer(event):
        global zoomcycle
        if (event.delta > 0):
            if zoomcycle != 4: zoomcycle += 1
        elif (event.delta < 0):
            if zoomcycle != 0: zoomcycle -= 1
        crop(event)
        print("zoooom")
    root.bind("<MouseWheel>",zoomer)
else:
    None

if operatingSystem ==1: 
    def zoom_in(event):
        global zoomcycle
        if zoomcycle != 0: zoomcycle -= 1
        crop(event)
        print(zoomcycle)
        print(event.num)
    
    def zoom_out(event):
        global zoomcycle
        if zoomcycle != 4: zoomcycle += 1
        crop(event)
        print(zoomcycle)
        print(event.num)
    root.bind("<Button-4>",zoom_out)
    root.bind("<Button-5>",zoom_in)
else:
    None
    
                
def crop(event):
    global im
    global zimg_id
    global zoomcycle
    global canvas
    global zimg
    if zimg_id: canvas.delete(zimg_id)
    if (zoomcycle) != 0:
        x,y = event.x, event.y
        if zoomcycle == 1:
            tmp = im.crop((x-45,y-30,x+45,y+30))
        elif zoomcycle == 2:
            tmp = im.crop((x-30,y-20,x+30,y+20))
        elif zoomcycle == 3:
            tmp = im.crop((x-15,y-10,x+15,y+10))
        elif zoomcycle == 4:
            tmp = im.crop((x-6,y-4,x+6,y+4))
        size = 300,200
        zimg = ImageTk.PhotoImage(tmp.resize(size))
        zimg_id = canvas.create_image(event.x, event.y, image=zimg)
        print(zoomcycle)
canvas.bind("<Motion>",crop)

#root.bind("<MouseWheel>",zoomer) #use MouseWheel and function zoomer for Windows
#root.bind("<Button-4>",zoom_out)
#root.bind("<Button-5>",zoom_in)
#canvas.bind("<Motion>",crop)
# ---- /imported ----
    





def printcoord(event):
    global t
    global checkBox1
    global checkBox2
    global checkBox3
    global checkBox4
    global checkBox5
    global checkBox6
    global canvasWidth
    global canvasHeight
    global rectangle
    global start
    global drawn
    
    if (event.x <= canvasWidth) and (event.y<=canvasHeight):
        #only do action clicking on canvas
        #possibly try root.winfo_x() later
        if t==1:
            origin_green = "#5ba552"
            x_calix1.set(event.x)
            x_caliy1.set(event.y)
            px1, py1 = (event.x - 3), (event.y - 3)
            px2, py2 = (event.x + 3), (event.y + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=origin_green, tag="dot1")
            
            rectangle = canvas.create_rectangle
            start = event
            drawn = None
            
            
            checkBox1 = Label(root, text=u"\u2714")
            checkBox1.place(x=1370,y=50)
            t=t+1
            return None
        if t==2:
            origin_green = "#5ba552"
            x_calix2.set(event.x)
            x_caliy2.set(event.y)
            px1, py1 = (event.x - 3), (event.y - 3)
            px2, py2 = (event.x + 3), (event.y + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=origin_green, tag="dot2")
            checkBox2 = Label(root, text=u"\u2714")
            checkBox2.place(x=1390,y=50)
            t=t+1
            return None
        if t==3:
            origin_green = "#5ba552"
            y_calix1.set(event.x)
            y_caliy1.set(event.y)
            px1, py1 = (event.x - 3), (event.y - 3)
            px2, py2 = (event.x + 3), (event.y + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=origin_green, tag="dot3")
    #        explanation2.config(font = (None, None, 'bold'))
            checkBox3 = Label(root, text=u"\u2714")
            checkBox3.place(x=1370,y=70)
            t=t+1
            return None
        if t==4:
            origin_green = "#5ba552"
            y_calix2.set(event.x)
            y_caliy2.set(event.y)
            px1, py1 = (event.x - 3), (event.y - 3)
            px2, py2 = (event.x + 3), (event.y + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=origin_green, tag="dot4")
            checkBox4 = Label(root, text=u"\u2714")
            checkBox4.place(x=1390,y=70)
            t=t+1
            return None
        if t==5:
            origin_green = "#5ba552"
            x0.set(event.x) #when using global mouse position coordinates use x0.set(root.winfo_pointerx())
            y0.set(event.y)
            px1, py1 = (event.x - 3), (event.y - 3)
            px2, py2 = (event.x + 3), (event.y + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=origin_green, tag="dot5")
    #        explanation3.config(font = (None, None, 'bold'))
            checkBox5 = Label(root, text=u"\u2714")
            checkBox5.place(x=1370,y=90)
            t=t+1
            return None
        if t==6:
            point1_yellow = "#ede625"
            x1.set(event.x)
            y1.set(event.y)
            px1, py1 = (event.x - 3), (event.y - 3)
            px2, py2 = (event.x + 3), (event.y + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=point1_yellow, tag="dot6")
    #        explanation4.config(font = (None, None, 'bold'))
            checkBox6 = Label(root, text=u"\u2714")
            checkBox6.place(x=1370,y=110)
            t=t+1
            return None
    else:
        return None

def onGrow(event):  
    global rectangle
    global start
    global drawn 
    global t                  
    if t==2:
        canvas = event.widget
        if drawn: canvas.delete(drawn)
        objectId = rectangle(start.x, start.y, event.x, event.y)
        drawn = objectId
    else:
        return None
    
canvas.bind("<ButtonPress-1>", printcoord)
canvas.bind('<B1-Motion>',     onGrow) 

def reset():
    print(sys.platform)
    global t
    global objectId
    t = 1
    x0.set(0)
    y0.set(0)
    x1.set(0)
    y1.set(0)
    dx.set(0)
    dy.set(0)
    x_calix1.set(0)
    x_calix2.set(0)
    x_caliy1.set(0)
    x_caliy2.set(0)
    y_calix1.set(0)
    y_calix2.set(0)
    y_caliy1.set(0)
    y_caliy2.set(0)
    dx_calix.set(0)
    dy_calix.set(0)
    dx_caliy.set(0)
    dy_caliy.set(0)
    dx_microns.set(0)
    dy_microns.set(0)
    dx_microns_round.set(0)
    dy_microns_round.set(0)
    canvas.delete("dot1")
    canvas.delete("dot2")
    canvas.delete("dot3")
    canvas.delete("dot4")
    canvas.delete("dot5")
    canvas.delete("dot6")
    checkBox1.destroy()
    checkBox2.destroy()
    checkBox3.destroy()
    checkBox4.destroy()
    checkBox5.destroy()
    checkBox6.destroy()
    objectId.destroy()
    

def buttonRelease(event):
    global buttonPressed
    buttonPressed = 0
canvas.bind("<ButtonRelease-1>",buttonRelease)
    
def calculate():
    #Computing coordinates relative to photo frame
    dx.set(x1.get()-x0.get())
    dy.set(y1.get()-y0.get())
    dx_calix.set(abs(x_calix1.get()-x_calix2.get()))
    dy_calix.set(abs(x_caliy1.get()-x_caliy2.get()))
    dx_caliy.set(abs(y_calix1.get()-y_calix2.get()))
    dy_caliy.set(abs(y_caliy1.get()-y_caliy2.get()))
    dx_microns.set(calibrationLength_x.get()*dx.get()/dx_calix.get())
    dy_microns.set(calibrationLength_y.get()*dy.get()/dy_caliy.get())
    dx_microns_round.set("%.3f" % dx_microns.get())
    dy_microns_round.set("%.3f" % dy_microns.get())
    
    #Computing angle phi
#    phi = arctan()
    

def client_exit():
    mExit=messagebox.askyesno(title="Quit", message="Are You Sure?")
    if mExit>0:
        root.destroy()
        return

def sendtoArduino():
    calculate()
    global dy_microns
    if operatingSystem == 1:
        arduino = serial.Serial("/dev/ttyACM0")
    if operatingSystem == 2:
        arduino = serial.Serial('COM3')
    else:
        print("Select operationSystem")
    
    print(arduino.name)
#    arduino = serial.Serial('COM3') #COM3 is the usb port from the arduino, may vary

#    timeout=0.1 #arduino connectie maken
    if arduino.is_open == 1:                    
        print("usb working")   # no conflict on usb
    
    start = arduino.readline().decode().strip()
    print(start)
    
    translationRate = 500 #one rotation is 500 microns rotation using the 28BYJ-48 stepper motor
    stepsperRotation = 64*64 #one rotation is 64*64=4096 steps using the 28BYJ-48 stepper motor
    steps = dy_microns.get()/translationRate*stepsperRotation
#    steps = 5/translationRate*stepsperRotation
    distanceStr = str(steps)
    print ("steps to travel")
    print (steps)
    
    
    arduino.write(distanceStr.encode()) #newpos is the variable distance to travel
                 
    arduino.close()  
    print ("usb closed, program finished")



def sendValuetoArduino():
    global dy_microns
    if operatingSystem == 1:
        arduino = serial.Serial("/dev/ttyACM0")
    if operatingSystem == 2:
        arduino = serial.Serial('COM3')
    else:
        print("Select operationSystem")
    
    print(arduino.name)
#    arduino = serial.Serial('COM3') #COM3 is the usb port from the arduino, may vary

#    timeout=0.1 #arduino connectie maken
    if arduino.is_open == 1:                    
        print("usb working")   # no conflict on usb
    
    start = arduino.readline().decode().strip()
    print(start)
    
    translationRate = 500 #one rotation is 500 microns rotation using the 28BYJ-48 stepper motor
    stepsperRotation = 64*64 #one rotation is 64*64=4096 steps using the 28BYJ-48 stepper motor
    steps = moveMicrons.get()/translationRate*stepsperRotation
#    steps = 5/translationRate*stepsperRotation
    distanceStr = str(steps)
    print ("steps to travel")
    print (steps)
    
    
    arduino.write(distanceStr.encode()) #newpos is the variable distance to travel
                 
    arduino.close()  
    print ("usb closed, program finished")








def callESCP2client():
    print("callESCP2client")



    
                 

#Menu
menu = Menu(root)
root.config(menu=menu)
file = Menu(menu)
file.add_command(label="Open image", command=openImage)
file.add_command(label="Exit", command=client_exit)
menu.add_cascade(label="File", menu=file)
edit = Menu(menu)
edit.add_command(label="Execute ESCP2 client", command=callESCP2client)
edit.add_command(label="Show Text", command=reset)
menu.add_cascade(label="Edit", menu=edit)  


#undoButton = Button(root, text="undo", command=undo)
#undoButton.place(x=1000,y=390)


# ---- sidebar -----

#SELECT
explanation_h = Label(root, text="Select")
explanation_h.config(font=headerfont)
explanation_h.place(x=1100,y=20)

explanation1 = Label(root, text="borders of the horizontal calibration sample").place(x=1100,y=50)
explanation2 = Label(root, text="borders of the vertical calibration sample").place(x=1100,y=70)
explanation3 = Label(root, text="printed (0,0) point").place(x=1100,y=90)
explanation4 = Label(root, text="desired print location").place(x=1100,y=110)


#SETTINGS
settings_h = Label(root, text="Settings")
settings_h.config(font=headerfont)
settings_h.place(x=1100,y=150)

cali_comment = Label(root, text="Size of the calibration sample").place(x=1100,y=175)
cali_hor = Label(root, text="Horizontal").place(x=1100,y=205)
cali_ver = Label(root, text="Vertical").place(x=1100,y=225)
Label(root, text="microns").place(x=1350,y=205)
Label(root, text="microns").place(x=1350,y=225)
calibrateLengthx = Entry(root, textvariable=calibrationLength_x).place(x=1180,y=205)
calibrateLengthy = Entry(root, textvariable=calibrationLength_y).place(x=1180,y=225)


#CONTROL
control_h = Label(root, text="Control")
control_h.config(font=headerfont)
control_h.place(x=1100,y=255)

resetButton = Button(root, text="Reset", width=20, command=reset)         
resetButton.place(x=1100, y=290)
calcButton = Button(root, text="Calculate", width=20, command=calculate)         
calcButton.place(x=1100, y=320)
arduinoButton = Button(root, text="Send to Arduino", width=20, command=sendtoArduino)         
arduinoButton.place(x=1100, y=350)


#Calibrate platform
Label(root, text="Calibrate platform").place(x=1100,y=480)
moveArduino = Entry(root, textvariable=moveMicrons).place(x=1100,y=500)
ArduinoValueButton = Button(root, text="Move value (microns)", width=20, command=sendValuetoArduino)         
ArduinoValueButton.place(x=1300, y=500)
Label(root, text="Negative value: move inside printer").place(x=1100,y=530)
Label(root, text="Positive value: move towards observer").place(x=1100,y=550)


#OUTPUT
outputl_h = Label(root, text="Output")
outputl_h.config(font=headerfont)
outputl_h.place(x=1100,y=380)

Label(root, text=u"\u0394"+"x = ").place(x=1100,y=410)
Label(root, text=u"\u0394"+"y = ").place(x=1100,y=430)

output_dx = Label(root, textvariable=dx_microns_round)
output_dy = Label(root, textvariable=dy_microns_round)
output_dx.place(x=1130,y=410)
output_dy.place(x=1130,y=430)
Label(root, text="microns (fill in in ESCP2-client").place(x=1200,y=410)
Label(root, text="microns").place(x=1200,y=430)

#c0_comment = Label(root, text="(0,0) position")
#xc0 = Label(root, textvariable=x0).place(x=1140,y=250)
#xc0_comment = Label(root, text="x = ").place(x=1100,y=250)
#yc0 = Label(root, textvariable=y0).place(x=1140,y=270)
#yc0_comment = Label(root, text="y = ").place(x=1100,y=270)
#c0_comment.config(font=headerfont)
#c0_comment.place(x=1100,y=220)
#
#c1_comment = Label(root, text="Print position")
#xc1 = Label(root, textvariable=x1).place(x=1140,y=330)
#xc1_comment = Label(root, text="x = ").place(x=1100,y=330)
#yc1 = Label(root, textvariable=y1).place(x=1140,y=350)
#yc1_comment = Label(root, text="y = ").place(x=1100,y=350)
#c1_comment.config(font=headerfont)
#c1_comment.place(x=1100,y=300)
#
#
#d_comment = Label(root, text="Delta x/y")
#dxc = Label(root, textvariable=dx).place(x=1140,y=410)
#dxc_comment = Label(root, text="x = ").place(x=1100,y=410)
#dyc = Label(root, textvariable=dy).place(x=1140,y=430)
#dyc_comment = Label(root, text="y = ").place(x=1100,y=430)
#d_comment.config(font=headerfont)
#d_comment.place(x=1100,y=380)
#
#calibrate_comment = Label(root, text="Calibration x axis")
#calibratex1 = Label(root, textvariable=x_calix1).place(x=1340,y=250)
#calibratex2 = Label(root, textvariable=x_calix2).place(x=1380,y=250)
#calibratex_comment = Label(root, text="x = ").place(x=1300,y=250)
#calibratey1 = Label(root, textvariable=x_caliy1).place(x=1340,y=270)
#calibratey2 = Label(root, textvariable=x_caliy2).place(x=1380,y=270)
#calibratey_comment = Label(root, text="y = ").place(x=1300,y=270)
#calibrate_comment.config(font=headerfont)
#calibrate_comment.place(x=1300,y=220)
#
#calibrate_comment = Label(root, text="Calibration y axis")
#calibratex1 = Label(root, textvariable=y_calix1).place(x=1340,y=330)
#calibratex2 = Label(root, textvariable=y_calix2).place(x=1380,y=330)
#calibratex_comment = Label(root, text="x = ").place(x=1300,y=330)
#calibratey1 = Label(root, textvariable=y_caliy1).place(x=1340,y=350)
#calibratey2 = Label(root, textvariable=y_caliy2).place(x=1380,y=350)
#calibratey_comment = Label(root, text="y = ").place(x=1300,y=350)
#calibrate_comment.config(font=headerfont)
#calibrate_comment.place(x=1300,y=300)
#
##delta x axis
#dxcalibratex = Label(root, textvariable=dx_calix).place(x=1430,y=250)
#dxcalibratey = Label(root, textvariable=dy_calix).place(x=1430,y=270)
#
##delta y axis
#dycalibratex = Label(root, textvariable=dx_caliy).place(x=1430,y=330)
#dycalibratey = Label(root, textvariable=dy_caliy).place(x=1430,y=350)
#
##output in microns
#output_dx = Label(root, textvariable=dx_microns)
#output_dy = Label(root, textvariable=dy_microns)
#output_dx.place(x=1300,y=410)
#output_dy.place(x=1300,y=430)
#output_comment = Label(root, text="Output")
#output_comment.config(font=headerfont)
#output_comment.place(x=1300,y=380)

root.mainloop()

# ---- TO DO ----
#using scrolling to zoom whole picture
#keep click position 
