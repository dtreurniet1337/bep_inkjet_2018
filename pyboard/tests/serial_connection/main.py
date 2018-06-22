from serial_listener import SerialListener

serial_listener = SerialListener()

counter = 0
while True:

    # Get message
    response = serial_listener.get_message()
    #print('received #%s: %s'%(counter, response))

    # Send it back
    f = serial_listener.send_message('ack %s: %s'%(counter, response))
    if not f:
        print(f)
    print('\n')

    counter += 1
