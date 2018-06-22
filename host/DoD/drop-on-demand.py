#!/usr/bin/python3

"""
Micro positioning tool for printing dropplets using the EPSON xp235 positioning platform

BEP PME 06 Hacking a commercial inkjet printer

Author:     R. Slingerland
Date:       02-06-2017
Version:    1.0

Edited January 2018 by A. Matser

- Updated Arduino code
- Pick second dot to get line start and end location

Future todo's
- Make last dot disappear when clicking reset
- draw line between one-to-last and last dot for further clarity in software
- create a full manual

"""

# ---- Import modules ----
from tkinter import *
from tkinter import Tk, Label, StringVar, IntVar, DoubleVar, Entry, Canvas, Scrollbar, Button, Menu, Toplevel, Text, OptionMenu
from PIL import Image
from PIL import ImageTk
from tkinter import filedialog, messagebox
from os import *
import os
import serial
import sys
from numpy import arctan, pi, sin, cos, tan, arcsin, arccos
#from main import *
from time import sleep

#create the window
root = Tk()

def sleepTime(time, text):
    print("--- Start, now wait " + str(time) + " seconds for " + text + ".")
    sleep(time)
    print("--- End of waiting for " + text + ".") 

def arduino_init(): # Abel addition
    global operatingSystem
    global arduino
    global timeToPrint, timeToStep, timeToWait

    #Operating system choice
    #Linux = 1
    #Windows = 2
    #Necessary for Arduino settings
    if str(sys.platform) == "win32":
        operatingSystem = 2
        print("OS Windows 32")
    elif str(sys.platform) == "linux":
        operatingSystem = 1
        print("OS Linux")
    else: 
        operatingSystem = input('Select operating system number: Linux (1), Windows 32 (2): ')
    
   # Path Arduino
    linuxpathList = [ "/dev/ttyUSB0" , "/dev/ttyUSB1" , "/dev/ttyACM0" , "/dev/ttyACM1" , "/dev/ttyACM2" , "/dev/ttyACM3" ] # possible connection paths for Abel

    if operatingSystem == 1:
        ### NEW ### automatically picks right path for Linux
        for k in range(len(linuxpathList)):
            try:
                arduino = serial.Serial(linuxpathList[k])
                if arduino.is_open == 1:                    
                    print("USB connection to Arduino working for " + str(linuxpathList[k]))
                    linuxpath = linuxpathList[k]
                    k = len(linuxpathList) # Abel this does not seem to work yet.
            except:
                pass
                #print( "USB connection to Arduino NOT working for " + str(linuxpathList[k]))
        
        try:
            if arduino.is_open == 1:
                pass
        except:
            print("0002: USB connection to Arduino NOT working, check in terminal with 'dmesg' if it is connected")
        
    elif operatingSystem == 2:
        arduino = serial.Serial('COM3')
    else:
        print("Select operating system")

    timeToPrint = 18 # measure this before printing, otherwise you will move arduino while printer is still printing
    timeToStep = 3
    timeToWait = 1

arduino_init()


#imagePath = "substrate.png"
imagePath = StringVar()
imagePath.set("./initial_image.JPG")
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

x2 = IntVar() #Abel print line second dot
y2 = IntVar()
x2.set(0)
y2.set(0)

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

dx1_microns_round = DoubleVar()
dy1_microns_round = DoubleVar()
dx1_microns_round.set(0)
dy1_microns_round.set(0)

dx2_microns_round = DoubleVar()
dy2_microns_round = DoubleVar()
dx2_microns_round.set(0)
dy2_microns_round.set(0)

dx_microns_round0 = DoubleVar()
dx_microns_round0.set(0)

moveMicrons = DoubleVar()
moveMicrons.set(100)

theta = DoubleVar()
theta.set(0)
theta_deg = DoubleVar()
theta_deg.set(0)

inputESCP2client1 = DoubleVar()
inputESCP2client1.set(0)
inputESCP2client2 = DoubleVar()
inputESCP2client2.set(0)

xstartOrigin = 166000 # absolute x position of the origin (standard value in ESCP2 client = 166000 microns which is in the middle of the platform)

widget_heigt = 100 #heigth of widgets

t_init = 1 #7 for rotate on 1 for rotate off
t = t_init #printcoord variable
#buttonPressed = 1

#modify root window
root.title("Drop-on-Demand")
#w, h = root.winfo_screenwidth(), root.winfo_screenheight()
w,h = 1500,800
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
    canvas.bind("<Motion>",crop)
    canvas.bind("<ButtonPress-1>", printcoord)
    canvas.bind('<B1-Motion>',     onGrow)
    reset()
    
def rotateImage(angle):
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
    im = im.rotate(angle*180/pi)
    photo = ImageTk.PhotoImage(im)
    image = canvas.create_image(0,0, anchor=NW, image=photo)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    canvas.config(scrollregion=canvas.bbox(ALL))
    xscrollbar.config(command=canvas.xview)
    yscrollbar.config(command=canvas.yview)
    canvas.bind("<Motion>",crop)
    canvas.bind("<ButtonPress-1>", printcoord)
    canvas.bind('<B1-Motion>',     onGrow)
#    t=1

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
    root.bind("<MouseWheel>",zoomer)
else:
    None

if operatingSystem ==1: 
    def zoom_in(event):
        global zoomcycle
        if zoomcycle != 0: zoomcycle -= 1
        crop(event)
    
    def zoom_out(event):
        global zoomcycle
        if zoomcycle != 4: zoomcycle += 1
        crop(event)
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
    global checkBox7
    global checkBox8
    global canvasWidth
    global canvasHeight
    global rectangle
    global line
    global start
    global drawn
    global theta
    
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
            checkBox7 = Label(root, text=u"\u2714")
            checkBox7.place(x=1370,y=80)
            t=8
            return None
        
        if t==8:
            line_purple = "#e800e8"
            line_x2.set(int(canvas.canvasx(event.x)))
            line_y2.set(int(canvas.canvasy(event.y)))
            px1, py1 = (line_x2.get() - 3), (line_y2.get() - 3)
            px2, py2 = (line_x2.get() + 3), (line_y2.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=line_purple, tag="dot8")
            theta.set(arctan((line_y1.get()-line_y2.get())/(line_x2.get()-line_x1.get())))
            theta_deg.set(theta.get()*180/pi)
            checkBox8 = Label(root, text=u"\u2714")
            checkBox8.place(x=1390,y=80)
            rotateImage(-theta.get())
            t=1
            return None
               



                   
                                  
        if t==1:
            calibratex_blue = "#00008B"
            x_calix1.set(int(canvas.canvasx(event.x)))
            x_caliy1.set(int(canvas.canvasy(event.y)))
            px1, py1 = (x_calix1.get() - 3), (x_caliy1.get() - 3)
            px2, py2 = (x_calix1.get() + 3), (x_caliy1.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=calibratex_blue, tag="dot1")
            
            #rectangle = canvas.create_rectangle
            #start = event
            #drawn = None
            
            
            checkBox1 = Label(root, text=u"\u2714")
            checkBox1.place(x=1370,y=100)
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
            checkBox2.place(x=1390,y=100)
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
            checkBox3.place(x=1370,y=120)
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
            checkBox4.place(x=1390,y=120)
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
            checkBox5.place(x=1370,y=140)
            t=6
            return None
        if t==6:
            point1_yellow = "#ede625"
            x1.set(int(canvas.canvasx(event.x)))
            print("x1: "+str(x1.get()))
            y1.set(int(canvas.canvasy(event.y)))
            print("y1: "+str(y1.get()))
            px1, py1 = (x1.get() - 3), (y1.get() - 3)
            px2, py2 = (x1.get() + 3), (y1.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=point1_yellow, tag="dot6")
    #        explanation4.config(font = (None, None, 'bold'))
            checkBox6 = Label(root, text=u"\u2714")
            checkBox6.place(x=1370,y=160)
            t=9
            return None
        if t==9:
            point2_yellow = "#ede625"
            x2.set(int(canvas.canvasx(event.x)))
            print("x2: "+str(x2.get()))
            x2.set(x2.get())
            y2.set(int(canvas.canvasy(event.y)))
            print("y2: "+str(y2.get()))
            px1, py1 = (x2.get() - 3), (y2.get() - 3)
            px2, py2 = (x2.get() + 3), (y2.get() + 3)
            canvas.create_oval(px1, py1, px2, py2, fill=point2_yellow, tag="dot6")
    #        explanation4.config(font = (None, None, 'bold'))
            checkBox6 = Label(root, text=u"\u2714")
            checkBox6.place(x=1390,y=160)
            t=10
            return None
    else:
        return None

def onGrow(event):
    """
    Function for drawing a rectangle for calibration (disabled)
    
    """  
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
#canvas.bind('<B1-Motion>',     onGrow) onGrow disabled

def reset():
    global t
    global t_init
    t = t_init
    x0.set(0)
    y0.set(0)
    x1.set(0)
    y1.set(0)
    x2.set(0) #Abel line
    y2.set(0)
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
    dx1_microns_round.set(0)
    dy1_microns_round.set(0)
    dx2_microns_round.set(0)
    dy2_microns_round.set(0)
    dx_microns_round0.set(0)
    inputESCP2client1.set(0)
    inputESCP2client2.set(0)
    rotateImage(0)
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
    if rotation_var.get()=="on":
        checkBox7.destroy()
        checkBox8.destroy()
        checkBox1.destroy()
        checkBox2.destroy()
        checkBox3.destroy()
        checkBox4.destroy()
        checkBox5.destroy()
        checkBox6.destroy()
    else:
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

    for k in range(2):
        if k==0: ### dot 1 of line
            dx.set(x1.get()-x0.get())
            dy.set(y1.get()-y0.get())
        if k==1: ### dot 2 of line
            dx.set(x2.get()-x0.get())
            dy.set(y2.get()-y0.get())

        #Computing coordinates relative to photo frame
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
        dy_microns.set(-calibrationLength_y.get()*dy.get()/dy_caliy.get())
        dx_microns_corr.set(dx_microns.get())
        dy_microns_corr.set(dy_microns.get())
        dx_microns_round.set("%.3f" % dx_microns.get())
        dy_microns_round.set("%.3f" % dy_microns.get())
        dx_microns_round0.set("%.f" % dx_microns.get())

        if k==0: ### dot 1 of line
            dx1_microns_round.set("%.3f" % dx_microns.get())
            print("dx1_microns_round: " + str(dx1_microns_round.get()))
            dy1_microns_round.set("%.3f" % dy_microns.get())
            inputESCP2client1.set(xstartOrigin-dx_microns_round0.get())
            #print("inputESCP2client1: " + str(inputESCP2client1.get()))
        if k==1: ### dot 2 of line
            dx2_microns_round.set("%.3f" % dx_microns.get())
            print("dx2_microns_round: " + str(dx2_microns_round.get()))
            dy2_microns_round.set("%.3f" % dy_microns.get())
            inputESCP2client2.set(xstartOrigin-dx_microns_round0.get())
            #print("inputESCP2client2: " + str(inputESCP2client2.get()))
        
    

def client_exit():
    mExit=messagebox.askyesno(title="Quit", message="Are You Sure?")
    if mExit>0:
        root.destroy()
        return

def sendtoArduino():
    print("sendtoArduino")
    calculate()
    global dy_microns
    #print(arduino.name)
    #sleepTime(0.1, "Arduino")
    
    if arduino.is_open == 1:                    
        print("USB connection to Arduino working")   # no conflict on usb
    else:
        print("Open up Arduino!")
        arduino.open()
        sleepTime(timeToWait, "Arduino")
        if arduino.is_open == 1:                    
            print("USB connection to Arduino working")   # no conflict on usb
        else:
            print( "USB connection to Arduino NOT working")
    
    try:
        # print("Read Arduino // disabled")
        print("Wait for Arduino start")
        sleep(timeToWait)
        start = ""
        while start != "Start":
            start = arduino.readline().decode().strip() # can give errors because there is nothing to print
        print("Arduino: " + start)
    except:
        print("Port " + arduino.name + " NOT really open.")

    translationRate = 500 #one rotation is 500 microns
    stepsperRotation = 200*16 #one rotation is 200*16=3200 steps using the NEMA-17 stepper motor
    steps = round(dy_microns.get()/translationRate*stepsperRotation)
    distanceStr = str(steps)
    print ("steps to travel " + distanceStr)

    arduino.write(distanceStr.encode())
    
    try:
        # sleepTime(timeToStep, "stepping") # could be replaced by read if the arduino prints text in loop after stepping
        # print("Read Arduino // disabled")
        print("Wait for Arduino end")
        sleep(timeToWait)
        end = ""
        while end != "End":
            end = arduino.readline().decode().strip() # can give errors because there is nothing to print
        print("Arduino: " + end)
    except:
        print("Port " + arduino.name + " NOT really open.")

    arduino.close()  # if not closed, you can't print
    print ("usb closed, program finished")

def sendValuetoArduino():
    print("sendValuetoArduino")
    global moveMicrons
    if arduino.is_open == 1:                    
        print("USB connection to Arduino working")   # no conflict on usb
    else:
        print("Open up Arduino!")
        arduino.open()
        sleepTime(timeToWait, "Arduino")
        if arduino.is_open == 1:                    
            print("USB connection to Arduino working")   # no conflict on usb
        else:
            print( "USB connection to Arduino NOT working")
    
    try:
        # print("Read Arduino // disabled")
        print("Wait for Arduino start")
        sleep(timeToWait)
        start = ""
        while start != "Start":
            start = arduino.readline().decode().strip() # can give errors because there is nothing to print
        print("Arduino: " + start)
    except:
        print("Port " + arduino.name + " NOT really open.")

    translationRate = 500 #one rotation is 500 microns
    stepsperRotation = 200*16 #one rotation is 200*16=3200 steps using the NEMA-17 stepper motor
    steps = round(moveMicrons.get()/translationRate*stepsperRotation)
    distanceStr = str(steps)
    print ("steps to travel " + distanceStr)
  
    arduino.write(distanceStr.encode())
    
    try:
        # sleepTime(timeToStep, "stepping") # could be replaced by read if the arduino prints text in loop after stepping
        # print("Read Arduino // disabled")
        print("Wait for Arduino end")
        sleep(timeToWait)
        end = ""
        while end != "End":
            end = arduino.readline().decode().strip() # can give errors because there is nothing to print
        print("Arduino: " + end)
    except:
        print("Port " + arduino.name + " NOT really open.")

    arduino.close()  # if not closed, you can't print
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
explanation_h.place(x=1100,y=50)
#explanation_h.grid(row=0, column=3, sticky=N)

explanation0 = Label(root, text="2 points on the printline").place(x=1100,y=80)
explanation1 = Label(root, text="borders of the horizontal calibration sample").place(x=1100,y=100)
explanation2 = Label(root, text="borders of the vertical calibration sample").place(x=1100,y=120)
explanation3 = Label(root, text="printed (0,0) point").place(x=1100,y=140)
explanation4 = Label(root, text="desired print location").place(x=1100,y=160)

#explanation1 = Label(root, text="borders of the horizontal calibration sample").grid(row=0, column =3, sticky=NW)
#explanation2 = Label(root, text="borders of the vertical calibration sample").grid(row=0, column =3, sticky=NW)
#explanation3 = Label(root, text="printed (0,0) point").grid(row=0, column =3, sticky=NW)
#explanation4 = Label(root, text="desired print location").grid(row=0, column =3, sticky=NW)


#SETTINGS
settings_h = Label(root, text="Settings")
settings_h.config(font=headerfont)
settings_h.place(x=1100,y=widget_heigt+100)

# Create a Tkinter variable
rotation_var = StringVar()
 
# Dictionary with options
choices = { 'on','off'}
rotation_var.set('off') # set the default option
 
popupMenu = OptionMenu(root, rotation_var, *choices)
Label(root, text="Rotation").place(x=1100,y=widget_heigt+130)
popupMenu.place(x=1180, y=widget_heigt+130)
 
# on change dropdown value
def change_dropdown(*args):
    global t
    if rotation_var.get()=="on":
        t=7
    elif rotation_var.get()=="off":
        t=1
    else:
        return None
 
# link function to change dropdown
rotation_var.trace('w', change_dropdown)




#Change Image Magnification factor
Label(root, text="Image Magnification Factor").place(x=1100,y=widget_heigt+160)
Label(root, text="IMF").place(x=1100,y=widget_heigt+190)
Entry(root, textvariable=imageMagnification).place(x=1180, y=widget_heigt+190)
Button(root, text="Apply", width=10, command=reloadImage).place(x=1350,y=widget_heigt+190)


cali_comment = Label(root, text="Size of the calibration sample").place(x=1100,y=widget_heigt+225)
cali_hor = Label(root, text="Horizontal").place(x=1100,y=widget_heigt+255)
cali_ver = Label(root, text="Vertical").place(x=1100,y=widget_heigt+275)
Label(root, text="microns").place(x=1350,y=widget_heigt+255)
Label(root, text="microns").place(x=1350,y=widget_heigt+275)
calibrateLengthx = Entry(root, textvariable=calibrationLength_x).place(x=1180,y=widget_heigt+255)
calibrateLengthy = Entry(root, textvariable=calibrationLength_y).place(x=1180,y=widget_heigt+275)


#CONTROL
control_h = Label(root, text="Control")
control_h.config(font=headerfont)
control_h.place(x=1100,y=widget_heigt+305)

resetButton = Button(root, text="Reset", width=20, command=reset)         
resetButton.place(x=1100, y=widget_heigt+340)
calcButton = Button(root, text="Calculate", width=20, command=calculate)         
calcButton.place(x=1100, y=widget_heigt+370)
arduinoButton = Button(root, text="Send to Arduino", width=20, command=sendtoArduino)         
arduinoButton.place(x=1100, y=widget_heigt+400)

#OUTPUT
outputl_h = Label(root, text="Diagonal line")
outputl_h.config(font=headerfont)
outputl_h.place(x=1100,y=widget_heigt+430)

### dot 1 of line ###
Label(root, text=u"\u0394"+"x1 = ").place(x=1100,y=widget_heigt+460)
Label(root, text=u"\u0394"+"y1 = ").place(x=1100,y=widget_heigt+480)

output_dx1 = Entry(root, textvariable=dx1_microns_round)
output_dy1 = Entry(root, textvariable=dy1_microns_round)
output_dx1.place(x=1180,y=widget_heigt+460)
output_dy1.place(x=1180,y=widget_heigt+480)
Label(root, text="microns").place(x=1350,y=widget_heigt+460)
Label(root, text="microns").place(x=1350,y=widget_heigt+480)
output_dx1.configure(state="readonly")
output_dy1.configure(state="readonly")

### dot 2 of line ###
Label(root, text=u"\u0394"+"x2 = ").place(x=1100,y=widget_heigt+505)
Label(root, text=u"\u0394"+"y2 = ").place(x=1100,y=widget_heigt+525)

output_dx2 = Entry(root, textvariable=dx2_microns_round)
output_dy2 = Entry(root, textvariable=dy2_microns_round)
output_dx2.place(x=1180,y=widget_heigt+505)
output_dy2.place(x=1180,y=widget_heigt+525)
Label(root, text="microns").place(x=1350,y=widget_heigt+505)
Label(root, text="microns").place(x=1350,y=widget_heigt+525)
output_dx2.configure(state="readonly")
output_dy2.configure(state="readonly")

### dot 1 of line ###
output_comment = Label(root, text="Single drop:")
output_comment.config(font=headerfont)
output_comment.place(x=1100,y=widget_heigt+555)

Label(root, text="x1 = ").place(x=1100,y=widget_heigt+585)

output = Entry(root, textvariable=inputESCP2client1)
output.place(x=1180,y=widget_heigt+585)
output.configure(state="readonly")

Label(root, text="microns").place(x=1350,y=widget_heigt+585)

### dot 2 of line ###

# Label(root, text="x2 = ").place(x=1100,y=widget_heigt+610)

# output = Entry(root, textvariable=inputESCP2client2)
# output.place(x=1180,y=widget_heigt+610)
# output.configure(state="readonly")

# Label(root, text="microns").place(x=1350,y=widget_heigt+610)

root.mainloop()


# ---- TO DO ----
#using scrolling to zoom whole picture
#keep click position 