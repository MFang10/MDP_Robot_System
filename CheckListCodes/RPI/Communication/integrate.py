from rfcomm_server import *
from arduino_interface import *
from collections import deque
import time
import threading

bt = rfcomm_server()
bt.connect_bt()
btQ = deque() # ard write to btQ, bt read from btQ
bt_interval = 0.5

ard = arduino_interface()
ard.connect()
ardQ = deque()
ard_interval = 0.5

def decode_dir(bt_msg):
    if bt_msg == "w":
        return b'w'
    elif bt_msg == "a":
        return b'a'
    elif bt_msg == "s":
        return b's'
    elif bt_msg == "d":
        return b'd'
    return b'na'

## Read from tablet
def bt_read():
    while 1:
        curByte = bt.read()
        if len(curByte) > 0:
            ardQ.append(str(curByte))
            print("Received: " + str(curByte) + " at " + str(time.time()))
        time.sleep(bt_interval)

## Write to tablet
def bt_write():
    while 1:
        time.sleep(bt_interval)
        if len(btQ) > 0:
            msg = btQ.popleft()
            bt.write("Ack " + msg)
            print("Ack " + msg + " at " + str(time.time()))
            
## Read from arduino
def ard_read():
    while 1:
        cur_msg = ard.read()
        if len(cur_msg) > 0:
            btQ.append(str(cur_msg))
            print("Received: " + str(cur_msg) + " at " + str(time.time()))
        time.sleep(ard_interval)

## Write to arduino
def ard_write():
    while 1:
        time.sleep(ard_interval)
        if len(ardQ) > 0:
            msg = ardQ.popleft()
            command = decode_dir(msg)
            print("Sent to arduino " + msg + " at " + str(time.time()))
            #ard.write(b'w')
            if command != b'na':
                ard.write(command)
                print("Sent to arduino: " + str(command))
            else:
                pass
                #ard.write(b'd')
            
            
        

threading.Thread(target = bt_read).start()
threading.Thread(target = bt_write).start()
threading.Thread(target = ard_read).start()
threading.Thread(target = ard_write).start()



