#!/usr/bin/env python3

import asyncio
import websockets
# from arduino_interface import *
from collections import deque
import time
import threading

# ard = arduino_interface()
# ard.connect()
pcQ = deque()
rpiQ = deque()
# ard_interval = 0.5

def decode_dir(ws_msg):
    if ws_msg == "w":
        return b'w'
    elif ws_msg == "a":
        return b'a'
    elif ws_msg == "s":
        return b's'
    elif ws_msg == "d":
        return b'd'
    elif ws_msg == "c": #calibration
        return b'c' 
    elif ws_msg == "f": #force stop robot movement
        return b'f'
    return b'na'

## Read from arduino
def ard_read():
    while 1:
        cur_msg = ard.read()
        if len(cur_msg) > 0:
            pcQ.append(str(cur_msg))
            print("Received: " + str(cur_msg) + " at " + str(time.time()))
        time.sleep(ard_interval)

## Write to arduino
def ard_write(msg):
    time.sleep(ard_interval)
    # msg = connection()
    # print(msg)
    command = decode_dir(msg)
    print("Sent to arduino " + msg + " at " + str(time.time()))
    # ard.write(b'd')
    if command != b'na':
        # ard.write(command)
        print("Sent to arduino: " + str(command))
    else:
        pass
            #ard.write(b'd')
            

async def connectionMaster(websocket, path):
	while 1:
		connection = await websocket.recv()
		# msg = (decode_dir(connection))
		print(connection)
		# ard_write(connection)
		sensorReading = "test"
		await websocket.send(sensorReading)


#change localhost to RPi IP Address (RPi will be the server)
start_server = websockets.serve(connectionMaster, '192.168.5.5', 8765) 

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
threading.Thread(target = ard_read).start()
threading.Thread(target = ard_write).start()
