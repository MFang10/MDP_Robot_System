'''
CZ3004 MDP 18/19 S1 Group 5
Algorithm > FinalSystem > rfcomm_server.py
By: Fang Meiyi

Module for setting up a RFCOMM server for Bluetooth communication.

'''

import bluetooth

class rfcomm_server(object):
    def __init__(self):
        self.server_sock = None
        
    def connect_bt(self):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.port = 6 ## port 6 used as the serial port
        self.server_sock.bind(("", self.port))
        self.server_sock.listen(1)
        
        self.client_sock, self.address = self.server_sock.accept()
        print("Accepted connection from " + str(self.address))
        
    def write(self, msg):
        encoded_msg = msg.encode('utf-8')   # encoding
        self.client_sock.send(msg)
        
    def read(self):
        data = self.client_sock.recv(1024)
        return str(data, 'utf-8')  # decoding
    
    def disconnect(self):
        self.client_sock.close()
        self.server_sock.close()
        
        
    