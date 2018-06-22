### not used yet, but would be beneficial for drop-on-demand and main_gui to access the same file



import serial

operatingSystem = 1
arduino = None
timeToPrint = 18
timeToStep = 3


def arduino_init():
    print("start arduino_init()")
    # global operatingSystem
    # global arduino
    # global timeToPrint, timeToStep

    # #Operating system choice
    # #Linux = 1
    # #Windows = 2
    # #Necessary for Arduino settings
    # if str(sys.platform) == "win32":
    #     operatingSystem = 2
    #     print("OS Windows 32")
    # elif str(sys.platform) == "linux":
    #     operatingSystem = 1
    #     print("OS Linux")
    # else: 
    #     operatingSystem = input('Select operating system number: Linux (1), Windows 32 (2): ')

    # print("start arduino_init()")
    
    # # Path Arduino
    # linuxpathList = []
    # linuxpathList = [ "/dev/ttyUSB0" , "/dev/ttyUSB1" , "/dev/ttyACM0" , "/dev/ttyACM1" ]
    # linuxpath = linuxpathList[3]

    # if operatingSystem == 1:
    #     ### NEW ###
    #     # for k in range(len(linuxpathList)):
    #     #     try:
    #     #         arduino = serial.Serial(linuxpathList[k])
    #     #         if arduino.is_open == 1:                    
    #     #             print("USB connection to Arduino working for " + str(linuxpathList[k]))
    #     #             linuxpath=linuxpathList[k]
    #     #             k = len(linuxpathList)
    #     #     except:
    #     #         print( "USB connection to Arduino NOT working for " + str(linuxpathList[k]))

    #     ### OLD ###
    #     arduino = serial.Serial(linuxpath)
    #     # linuxpath = linuxpathList[k]
    #     # linuxpath = "/dev/ttyACM1"
    # elif operatingSystem == 2:
    #     arduino = serial.Serial('COM3')
    # else:
    #     print("Select operating system")

    # timeToPrint = 18 # measure this before printing, otherwise you will move arduino while printer is still printing
    # #maybe have this depend on done signal of lp?
    # timeToStep = 3

    # global operatingSystem
    # global arduino
    # global timeToPrint, timeToStep

    print("start arduino_init()")
    # Path arduino
    linuxpath0="/dev/ttyUSB0"
    linuxpath1="/dev/ttyUSB1"
    linuxpath2="/dev/ttyACM0"
    linuxpath3="/dev/ttyACM1"
    linuxpath=linuxpath2
    # test which path is available ABEL

    # ONLY FOR LINUX
    arduino = serial.Serial(linuxpath)
    print(arduino.name)
    operatingSystem=1
    
    timeToPrint = 18 # measure this before printing, otherwise you will move arduino while printer is still printing
    #maybe have this depend on done signal of lp?
    timeToStep = 3