from pyb import USB_VCP

class SerialListener(USB_VCP):
    def __init__(self):
        super().__init__()

    def get_message(self):
        try:
            while True:
                data = self.readline()
                if data != None:
                    return str(data.decode('ascii'))

        except Exception as e:
            return 'get_message() failed: '+str(e)


    def send_message(self, message):
        try:
            self.write(message.encode('ascii'))
            return True
        except Exception as e:
            return 'send_message() failed: '+str(e)
