#!/usr/bin/env python
'''
import asyncio
import websockets

async def connectionSlave():
    #server IP address
    #Change Localhost to RPi IP Address, PC will be client
    async with websockets.connect('ws://localhost:8762') as websocket:
        try:
            while 1:    
                #replace this part to let Algo send commands to RPi
                connection = input("Enter Commands: ")
                await websocket.send(connection)
                print(connection)
                command = await websocket.recv()
                print(command)
        except KeyboardInterrupt:
            print("closed")
            websocket.close()

asyncio.get_event_loop().run_until_complete(connectionSlave())
'''

#!/usr/bin/env python

import socket

class wifi_client(object):
    def __init__(self):
        self.TCP_IP = '192.168.5.5'
        self.TCP_PORT = 8788
        self.BUFFER_SIZE = 1024

    def connect_wifi(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.TCP_IP, self.TCP_PORT))

    def read(self):
        data = self.s.recv(self.BUFFER_SIZE)
        return str(data)

    def write(self, msg):
        self.s.send(msg)

    def disconnect(self):
        self.s.close()
