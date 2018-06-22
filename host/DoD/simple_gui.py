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
from tkinter import Tk, Label, StringVar, IntVar, DoubleVar, Entry, Canvas, Scrollbar, Button, Menu, Toplevel, Text
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
from os import *
import os
import serial
import sys
from numpy import arctan, pi, sin, cos, tan, arcsin, arccos
#from main import *

#create the window
root = Tk()

#Operating system
#Linux = 1
#Windows = 2
#Enables zoom function and arduino settings
if str(sys.platform) == "win32":
    operatingSystem = 2
    print("OS Windows")
elif str(sys.platform) == "linux":
    operatingSystem = 1
    print("OS Linux")
else: 
    operatingSystem = input('Select operating system number: Linux (1), Windows (2): ')


# ---- variables ----
#imagePath = "substrate.png"
imagePath = StringVar()
imagePath.set("/home/localadmin/Desktop/GUI/EPNCS-tweak/initial_image.JPG")
#imagePath = filedialog.askopenfilename(title='open')
imageMagnification = DoubleVar()
imageMagnification.set(0.25) #default 1/5, change when using a different camera

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

line_x1 = DoubleVar()
line_y1 = DoubleVar()
line_x2 = DoubleVar()
line_y2 = DoubleVar()
line_x1.set(0)
line_y1.set(0)
line_x2.set(0)
line_y2.set(0)


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

dx_calix_corr = DoubleVar()
dy_caliy_corr = DoubleVar()
dx_microns_corr = DoubleVar()
dy_microns_corr = DoubleVar()
dx_calix_corr.set(0)
dy_caliy_corr.set(0)
dx_microns_corr.set(0)
dy_microns_corr.set(0)

dy_corr = DoubleVar()
dx_corr= DoubleVar()
dy_corr.set(0)
dx_corr.set(0)

dx_microns = DoubleVar()
dy_microns = DoubleVar()
dx_microns.set(0)
dy_microns.set(0)

dx_microns_round = DoubleVar()
dy_microns_round = DoubleVar()
dx_microns_round.set(0)
dy_microns_round.set(0)

dx_microns_round0 = DoubleVar()
dx_microns_round0.set(0)

moveMicrons = DoubleVar()
moveMicrons.set(100)

theta = DoubleVar()
theta.set(0)
theta_deg = DoubleVar()
theta_deg.set(0)

inputESCP2client = DoubleVar()
inputESCP2client.set(0)

xstartOrigin = 166000 # absolute x position of the origin (standard value in ESCP2 client = 166000 microns which is in the middle of the platform)

t = 7 #printcoord variable
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
    global im_height
    global im_size
    global photo
    global canvas
    global xscrollbar
    global yscrollbar
    imagePath.set(openFilename())
    print(imagePath.get())
    canvas.destroy()  
    canvas = Canvas(root,height=canvasHeight,width=canvasWidth,xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
    canvas.place(x=canvasxPosition,y=canvasyPosition)
    im = Image.open(imagePath.get())
    im_width, im_height = im.size
    im = im.resize((int(im_width*imageMagnification.get()), int(im_height*imageMagnification.get())),Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(im)
    image = canvas.create_image(0,0, anchor=NW, image=photo)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    canvas.config(scrollregion=canvas.bbox(ALL))
    xscrollbar.config(command=canvas.xview)
    yscrollbar.config(command=canvas.yview)
    print("openImage")
    canvas.bind("<Motion>",crop)
    canvas.bind("<ButtonPress-1>", printcoord)
    canvas.bind('<B1-Motion>',     onGrow)
    reset()

def reloadImage():
    global imagePath
    global image
    global im
    global im_width
    global im_height
    global im_size
    global photo
    global canvas
    global xscrollbar
    global yscrollbar
    canvas = Canvas(root,height=canvasHeight,width=canvasWidth,xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
    canvas.place(x=canvasxPosition,y=canvasyPosition)
    im = Image.open(imagePath.get())
    im_width, im_height = im.size
    im = im.resize((int(im_width*imageMagnification.get()), int(im_height*imageMagnification.get())),Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(im)
    image = canvas.create_image(0,0, anchor=NW, image=photo)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    canvas.config(scrollregion=canvas.bbox(ALL))
    xscrollbar.config(command=canvas.xview)
    yscrollbar.config(command=canvas.yview)
    print("openImage")
    canvas.bind("<Motion>",crop)
    canvas.bind("<ButtonPress-1>", printcoord)
    canvas.bind('<B1-Motion>',     onGrow)
    reset()
    
def rotateImage():
    global imagePath
    global image
    global im
    global im_width
    global im_height
    global im_size
    global photo
    global canvas
    global xscrollbar
    global yscrollbar
    global t
    canvas.destroy()  
    canvas = Canvas(root,height=canvasHeight,width=canvasWidth,xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
    canvas.place(x=canvasxPosition,y=canvasyPosition)
    im = Image.open(imagePath.get())
    im_width, im_height = im.size
    im = im.resize((int(im_width*imageMagnification.get()), int(im_height*imageMagnification.get())),Image.ANTIALIAS)
    im = im.rotate(-theta.get()*180/pi)
    photo = ImageTk.PhotoImage(im)
    image = canvas.create_image(0,0, anchor=NW, image=photo)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    canvas.config(scrollregion=canvas.bbox(ALL))
    xscrollbar.config(command=canvas.xview)
    yscrollbar.config(command=canvas.yview)
    print("openImage")
    canvas.bind("<Motion>",crop)
    canvas.bind("<ButtonPress-1>", printcoord)
    canvas.bind('<B1-Motion>',     onGrow)
    t=1

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
im = im.resize((int(im_width*imageMagnification.get()), int(im_height*imageMagnification.get())),Image.ANTIALIAS)
photo = ImageTk.PhotoImage(im)
image = canvas.create_image(0,0, anchor=NW, image=photo)
canvas.grid(row=0, column=0, sticky=N+S+E+W)
canvas.config(scrollregion=canvas.bbox(ALL))

xscrollbar.config(command=canvas.xview)
yscrollbar.config(command=canvas.yview)
print(xscrollbar.get())

# ---- zoom function ----
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
        x,y = canvas.canvasx(event.x), canvas.canvasy(event.y)
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
        zimg_id = canvas.create_image(canvas.canvasx(event.x), canvas.canvasy(event.y), image=zimg)
        print(zoomcycle)
canvas.bind("<Motion>",crop)

#root.bind("<MouseWheel>",zoomer) #use MouseWheel and function zoomer for Windows
#root.bind("<Button-4>",zoom_out)
#root.bind("<Button-5>",zoom_in)
#canvas.bind("<Motion>",crop)
# ---- /zoom function ----
    





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
    global line
    global start
    global drawn
    global theta
    print("printcoord")
    
    if (event.x <= canvasWidth) and (event.y<=canvasHeight):
        #only do action clicking on canvas
        #possibly try root.winfo_x() later
        
                                  
                                  
                                  
        if t==7:
            line_purple = "#e800e8"
            line_x1.set(int(canvas.canvasx(event.x)))
            line_y1.set(int(canvas.canvasy(event.y)))
            px1, py1 = (line_x1.get() - 3), (line_y1.get() - 3)
            px2, py2 = (line_x1.get() + 3), (line_y1.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=line_purple, tag="dot7")
#            checkBox2 = Label(root, text=u"\u2714")
#            checkBox2.place(x=1390,y=50)
            t=8
            return None
        
        if t==8:
            line_purple = "#e800e8"
            line_x2.set(int(canvas.canvasx(event.x)))
            line_y2.set(int(canvas.canvasy(event.y)))
            px1, py1 = (line_x2.get() - 3), (line_y2.get() - 3)
            px2, py2 = (line_x2.get() + 3), (line_y2.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=line_purple, tag="dot8")
#            line = canvas.create_line
#            start = event
#            drawn = None
            canvas.create_line(line_x1.get(),line_y1.get(),line_x2.get(),line_y2.get(), tag="line")
#            checkBox2 = Label(root, text=u"\u2714")
#            checkBox2.place(x=1390,y=50)
            theta.set(arctan((line_y1.get()-line_y2.get())/(line_x2.get()-line_x1.get())))
            theta_deg.set(theta.get()*180/pi)
            t=10
            return None
               



                   
                                  
        if t==1:
            calibratex_blue = "#00008B"
            x_calix1.set(int(canvas.canvasx(event.x)))
            x_caliy1.set(int(canvas.canvasy(event.y)))
            px1, py1 = (x_calix1.get() - 3), (x_caliy1.get() - 3)
            px2, py2 = (x_calix1.get() + 3), (x_caliy1.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=calibratex_blue, tag="dot1")
            
            rectangle = canvas.create_rectangle
            start = event
            drawn = None
            
            
            checkBox1 = Label(root, text=u"\u2714")
            checkBox1.place(x=1370,y=50)
            t=2
            return None
        if t==2:
            calibratex_blue = "#00008B"
            x_calix2.set(int(canvas.canvasx(event.x)))
            x_caliy2.set(int(canvas.canvasy(event.y)))
            px1, py1 = (x_calix2.get() - 3), (x_caliy2.get() - 3)
            px2, py2 = (x_calix2.get() + 3), (x_caliy2.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=calibratex_blue, tag="dot2")
            checkBox2 = Label(root, text=u"\u2714")
            checkBox2.place(x=1390,y=50)
            t=3
            return None
        if t==3:
            calibratey_blue = "#1E90FF"
            y_calix1.set(int(canvas.canvasx(event.x)))
            y_caliy1.set(int(canvas.canvasy(event.y)))
            px1, py1 = (y_calix1.get() - 3), (y_caliy1.get() - 3)
            px2, py2 = (y_calix1.get() + 3), (y_caliy1.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=calibratey_blue, tag="dot3")
    #        explanation2.config(font = (None, None, 'bold'))
            checkBox3 = Label(root, text=u"\u2714")
            checkBox3.place(x=1370,y=70)
            t=4
            return None
        if t==4:
            calibratey_blue = "#1E90FF"
            y_calix2.set(int(canvas.canvasx(event.x)))
            y_caliy2.set(int(canvas.canvasy(event.y)))
            px1, py1 = (y_calix2.get() - 3), (y_caliy2.get() - 3)
            px2, py2 = (y_calix2.get() + 3), (y_caliy2.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=calibratey_blue, tag="dot4")
            checkBox4 = Label(root, text=u"\u2714")
            checkBox4.place(x=1390,y=70)
            t=5
            return None
        if t==5:
            origin_green = "#5ba552"
            x0.set(int(canvas.canvasx(event.x))) #when using global mouse position coordinates use x0.set(root.winfo_pointerx())
            y0.set(int(canvas.canvasy(event.y)))
            px1, py1 = (x0.get() - 3), (y0.get() - 3)
            px2, py2 = (x0.get() + 3), (y0.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=origin_green, tag="dot5")
    #        explanation3.config(font = (None, None, 'bold'))
            checkBox5 = Label(root, text=u"\u2714")
            checkBox5.place(x=1370,y=90)
            t=6
            return None
        if t==6:
            point1_yellow = "#ede625"
            x1.set(int(canvas.canvasx(event.x)))
            y1.set(int(canvas.canvasy(event.y)))
            px1, py1 = (x1.get() - 3), (y1.get() - 3)
            px2, py2 = (x1.get() + 3), (y1.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=point1_yellow, tag="dot6")
    #        explanation4.config(font = (None, None, 'bold'))
            checkBox6 = Label(root, text=u"\u2714")
            checkBox6.place(x=1370,y=110)
            t=10
            return None
    else:
        return None

def onGrow(event):  
    global rectangle
    global start
    global drawn 
    global canvas
    global line
    global t                  
    if t==2:
        canvas = event.widget
        if drawn: canvas.delete(drawn)
        objectId = rectangle(canvas.canvasx(start.x), canvas.canvasy(start.y), canvas.canvasx(event.x), canvas.canvasy(event.y), tag="rectangle")
        drawn = objectId
        print("start.x = %r start.y = %r event.x = %r event.y = %r" % (start.x, start.y, event.x, event.y))
    if t==8:
        canvas = event.widget
        if drawn: canvas.delete(drawn)
        objectId = line(canvas.canvasx(start.x), canvas.canvasy(start.y), canvas.canvasx(event.x), canvas.canvasy(event.y), tag="line")
        drawn = objectId
        print("start.x = %r start.y = %r event.x = %r event.y = %r" % (start.x, start.y, event.x, event.y))
    else:
        return None
    
canvas.bind("<ButtonPress-1>", printcoord)
canvas.bind('<B1-Motion>',     onGrow) 

def reset():
    global t
    print(xscrollbar.delta(10,10))
    t = 7
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
    theta.set(0)
    theta_deg.set(0)
    dx_microns_round.set(0)
    dy_microns_round.set(0)
    dx_microns_round0.set(0)
    inputESCP2client.set(0)
    canvas.delete("dot1")
    canvas.delete("dot2")
    canvas.delete("dot3")
    canvas.delete("dot4")
    canvas.delete("dot5")
    canvas.delete("dot6")
    canvas.delete("rectangle")
    canvas.delete("line")
    canvas.delete("dot7")
    canvas.delete("dot8")
    checkBox1.destroy()
    checkBox2.destroy()
    checkBox3.destroy()
    checkBox4.destroy()
    checkBox5.destroy()
    checkBox6.destroy()
    

def buttonRelease(event):
    global buttonPressed
    buttonPressed = 0
canvas.bind("<ButtonRelease-1>",buttonRelease)
    
def calculate():
    #Computing coordinates relative to photo frame
    dx.set(x1.get()-x0.get())
    dy.set(y1.get()-y0.get())
    dy_corr.set(dy.get()/cos(theta.get())+(dx.get()-dy.get()*tan(theta.get()))*cos(theta.get()))
    dx_corr.set((dx.get()-dy.get()*tan(theta.get()))*cos(theta.get()))
    dx_calix.set(abs(x_calix2.get()-x_calix1.get()))
    dy_calix.set(abs(x_caliy1.get()-x_caliy2.get()))
#    dx_calix_corr.set((dy_calix.get()-dx_calix.get()*tan(theta.get()))*cos(theta.get())+(dx_calix.get()/cos(theta.get()))) #corrected with respect to the print line
    dx_calix_corr.set(dx_calix.get()/cos(theta.get())) #corrected with respect to the print line
    dx_caliy.set(abs(y_calix1.get()-y_calix2.get()))
    dy_caliy.set(abs(y_caliy1.get()-y_caliy2.get()))
    dy_caliy_corr.set(dy_caliy.get()/cos(theta.get())) #corrected with respect to the print line
    dx_microns.set(calibrationLength_x.get()*dx.get()/dx_calix.get())
    dy_microns.set(calibrationLength_y.get()*dy.get()/dy_caliy.get())
    dx_microns_corr.set(dx_microns.get())
    dy_microns_corr.set(dy_microns.get())
    dx_microns_round.set("%.3f" % dx_microns.get())
    dy_microns_round.set("%.3f" % dy_microns.get())
    dx_microns_round0.set("%.f" % dx_microns.get())
    inputESCP2client.set(xstartOrigin+dx_microns_round0.get())
    

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
    steps = -dy_microns.get()/translationRate*stepsperRotation
#    steps = 5/translationRate*stepsperRotation
    distanceStr = str(steps)
    print ("steps to travel")
    print (steps)
    
    
    arduino.write(distanceStr.encode()) #newpos is the variable distance to travel
                 
    arduino.close()  
    print ("usb closed, program finished")

def sendValuetoArduino():
    global moveMicrons
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



def calibratePlatform():
    global moveMicrons
    print(moveMicrons.get())
    calibrate_window = Toplevel()
    calibrate_window.title("Calibrate platform")
    w, h = 300, 200
    calibrate_window.geometry("%dx%d+0+0" % (w, h))
    Label(calibrate_window, text="Move the platform (in microns)").place(x=10,y=10)
    Entry(calibrate_window, textvariable=moveMicrons).place(x=10,y=40)
    print(moveMicrons.get())
    ArduinoValueButton = Button(calibrate_window, text="Send to Arduino", width=20, command=sendValuetoArduino)         
    ArduinoValueButton.place(x=10, y=60)
    Label(calibrate_window, text="Negative value: move inside printer").place(x=10,y=100)
    Label(calibrate_window, text="Positive value: move towards observer").place(x=10,y=120)
    


    
                 

#Menu
menu = Menu(root)
root.config(menu=menu)
file = Menu(menu)
file.add_command(label="Open image", command=openImage)
file.add_command(label="Exit", command=client_exit)
menu.add_cascade(label="File", menu=file)
edit = Menu(menu)
edit.add_command(label="Execute ESCP2 client", command=callESCP2client)
edit.add_command(label="Calibrate platform", command=calibratePlatform)
menu.add_cascade(label="Edit", menu=edit)  


#undoButton = Button(root, text="undo", command=undo)
#undoButton.place(x=1000,y=390)


# ---- sidebar -----


#SELECT
explanation_h = Label(root, text="Select")
explanation_h.config(font=headerfont)
explanation_h.place(x=1100,y=20)
#explanation_h.grid(row=0, column=3, sticky=N)

explanation1 = Label(root, text="borders of the horizontal calibration sample").place(x=1100,y=50)
explanation2 = Label(root, text="borders of the vertical calibration sample").place(x=1100,y=70)
explanation3 = Label(root, text="printed (0,0) point").place(x=1100,y=90)
explanation4 = Label(root, text="desired print location").place(x=1100,y=110)

#explanation1 = Label(root, text="borders of the horizontal calibration sample").grid(row=0, column =3, sticky=NW)
#explanation2 = Label(root, text="borders of the vertical calibration sample").grid(row=0, column =3, sticky=NW)
#explanation3 = Label(root, text="printed (0,0) point").grid(row=0, column =3, sticky=NW)
#explanation4 = Label(root, text="desired print location").grid(row=0, column =3, sticky=NW)

Button(root, text="Rotate image", width=20, command=rotateImage).place(x=1400,y=70)

#SETTINGS
settings_h = Label(root, text="Settings")
settings_h.config(font=headerfont)
settings_h.place(x=1100,y=150)

#Change Image Magnification factor
Label(root, text="Image Magnification Factor = ").place(x=1100,y=175)
Entry(root, textvariable=imageMagnification).place(x=1300, y=175)
Button(root, text="Select", width=10, command=reloadImage).place(x=1300,y=200)


cali_comment = Label(root, text="Size of the calibration sample").place(x=1100,y=225)
cali_hor = Label(root, text="Horizontal").place(x=1100,y=255)
cali_ver = Label(root, text="Vertical").place(x=1100,y=275)
Label(root, text="microns").place(x=1350,y=255)
Label(root, text="microns").place(x=1350,y=275)
calibrateLengthx = Entry(root, textvariable=calibrationLength_x).place(x=1180,y=255)
calibrateLengthy = Entry(root, textvariable=calibrationLength_y).place(x=1180,y=275)


#CONTROL
control_h = Label(root, text="Control")
control_h.config(font=headerfont)
control_h.place(x=1100,y=305)

resetButton = Button(root, text="Reset", width=20, command=reset)         
resetButton.place(x=1100, y=340)
calcButton = Button(root, text="Calculate", width=20, command=calculate)         
calcButton.place(x=1100, y=370)
arduinoButton = Button(root, text="Send to Arduino", width=20, command=sendtoArduino)         
arduinoButton.place(x=1100, y=400)

#OUTPUT
outputl_h = Label(root, text="Output")
outputl_h.config(font=headerfont)
outputl_h.place(x=1100,y=430)

Label(root, text=u"\u0394"+"x = ").place(x=1100,y=460)
Label(root, text=u"\u0394"+"y = ").place(x=1100,y=480)

output_dx = Label(root, textvariable=dx_microns_round)
output_dy = Label(root, textvariable=dy_microns_round)
output_dx.place(x=1130,y=460)
output_dy.place(x=1130,y=480)
Label(root, text="microns").place(x=1200,y=460)
Label(root, text="microns").place(x=1200,y=480)

output_comment = Label(root, text="Fill in in ESCP2-client (microns):")
output_comment.config(font=headerfont)
output_comment.place(x=1100,y=530)

output = Entry(root, textvariable=inputESCP2client)
output.place(x=1100,y=580)
output.configure(state="readonly")



theta_label = Label(root, textvariable=theta_deg).place(x=1300,y=480)

root.mainloop()


# ---- TO DO ----
#using scrolling to zoom whole picture
#keep click position 
