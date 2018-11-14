import serial
# import RPi.GPIO as GPIO
import time
import binascii

# def blink(pin, direction):
#     GPIO.output(pin, GPIO.HIGH)
#     time.sleep(1)
#     return

class arduino_interface(object):
    def __init__(self):
        self.port = "/dev/ttyACM0"
        self.baudrate = 115200
        
    def connect(self):
        self.ser = serial.Serial(self.port, self.baudrate)
        #self.ser.write("Communication init ..")
        
    def write(self, msg):
        self.ser.write(msg)
        #print("Writing to arduino " + msg)
    
    def read(self):
        msg = self.ser.readline()
        return str(msg)[2:len(msg)]
   
    def disconnect(self):
        self.ser.close()
        

if __name__ == "__main__":
    print("Running main for arduino interface")
    ard = arduino_interface()
    ard.connect()
    while True:
        msg = ard.read()
        ard.write(b'w')
        print("Received " + msg)
        # if msg == "Hello From Arduino!":
        #     blink(11, "w")
    


'''
ser = serial.Serial("/dev/ttyACM0", 115200)  # double check ACM port number
ser.baudrate = 115200
def blink(pin, direction):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(1)
    return

    
while True:
    read_ser = ser.readline()
    print(read_ser)
    if read_ser == "Hello From Arduino!":
        blink(11,"w")
'''