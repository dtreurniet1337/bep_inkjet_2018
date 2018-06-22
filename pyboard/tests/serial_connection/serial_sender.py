import serial
import time

ser = serial.Serial('/dev/ttyACM0')
print('connected to %s'%(ser.name))


modes = ['auto', 'single']


def get_response():
    while True:
        data = ser.readline()
        if data != None:
            return data.decode('ascii')

def single():
    while True:
        command = input('command (enter "exit" to stop): ')
        if command == 'exit': break
        ser.write(command.encode('ascii'))
        response = get_response()
        print(response)


def auto():
    while True:
        filename = input('filename: ')
        try:
            f = open(filename, 'r')
            break
        except Exception as e:
            print('Error: %s'%(e))

    line_counter = 0
    for line in f.readlines():
        line_counter += 1
    f.close()

    print('Loaded %s with %s lines of code'%(filename, line_counter))
    input('Press any key to start...')

    f = open(filename, 'r')
    for command in f.readlines():
        if command[:2] != 'G1': continue
        print(command)
        ser.write(command.encode('ascii'))
        reponse = get_response()
    f.close()



while True:
    while True:
        mode = input('Select mode [single, auto]: ')
        if mode in modes: break
        else: print('Invalid mode...')
    if mode == 'auto':
        auto()
    if mode == 'single':
        single()
