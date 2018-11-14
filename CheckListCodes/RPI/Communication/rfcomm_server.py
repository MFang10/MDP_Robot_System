import bluetooth

class rfcomm_server(object):
    def __init__(self):
        self.server_sock = None
        
    def connect_bt(self):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.port = 4
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
        
        
    
'''
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = 4
server_sock.bind(("", port))
bd_addr = "38:A4:ED:7E:56:4C"
#rpi_client = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
#pi_client.connect((bd_addr, 4))
server_sock.listen(1)

client_sock, address = server_sock.accept()
print("Accepted connection from "+ str(address))

#rpi_client.send("hello!!")
data = client_sock.recv(1024)
print("received [%s]" % data)
client_sock.send("received" + str(data))


client_sock.close()
server_sock.close()
#rpi_client.close()
'''