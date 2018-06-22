from pyb import USB_VCP

class serialListener(USB_VCP):
    """
    This class takes care of all serial communication with the host machine.
    Most important functions are:
        get_message():      reads first command available and returns the decoded string
        send_message(str):  sends a message back to the host machine
    """

    def __init__(self):
        super().__init__()

    def get_message(self):
        try:
            data = self.readline()
            if data != None:
                return str(data.decode('ascii'))
        except Exception as e: return 'get_message() failed: '+str(e)
        return False


    def send_message(self, message):
        message = str(message)+'\n'
        try:
            self.write(message.encode('ascii'))
            return True
        except Exception as e: return 'send_message() failed: '+str(e)
