import socket
import Miuchiz
from PACKET_IDS import *
from threading import Thread
import struct
class Connection():
    def __init__(self, conn):
        self.conn = conn
        self.stage = 0
        self.characterData = None
        self.Character = None
    def recv(self, b):
        return self.conn.recv(b)
    def send(self, b):
        return self.conn.send(b)
    def close(self):
        return self.conn.close()

      

def HandleConnection(connection):
    c = connection
    connections.append(c)
    while c:
        try: raw = c.recv(8192)
        except: return
        if not raw: return
        formatted_data =  "".join("%02x " % b for b in raw)
        packet_id = struct.unpack('I', raw[0:4])[0]
        print('Packet ID 0x%x' % packet_id)
        print('Received:', formatted_data)
        
        if packet_id == CLIENT_INITIAL_PACKET:
            if connection.stage != 0:
                c.close()
                return
            connection.stage = 1
            print('Initial packet')

            #Two packets must be sent in order for every attempt
            #to be successful. The second packet has to be a login packet.
            
            resp = b''
            resp += struct.pack('I', (SERVER_INITIAL_PACKET)) #Packet ID
            resp += b'\x35\x00\x00\x00'
            resp += b'\x00\x00\x00\x00'
            resp += b'\x00\x00\x00\x00'
            resp += b'\x00\x00\x00\x00'
            resp += b'[Miuchiz Sync]\r\nVersion=1.0.0.67'
            resp += b'\x00'
            c.send(resp)

            #Start of login server packet
            resp = b''
            resp += struct.pack('I', (SERVER_LOGIN_PACKET)) #login packet id
            resp += b'\x10\x00\x00\x00' #Length (Includes the next section, which will be sent later)
            c.send(resp)

                
        elif packet_id == CLIENT_LOGIN_PACKET:
            if connection.stage != 1:
                c.close()
                return
            connection.stage = 2
            print('Login packet')
            STRING_LENGTH = 16
            username = raw[8 : raw.find(b'\x00', 8, 8 + STRING_LENGTH)].decode('UTF-8')
            password = raw[24 : raw.find(b'\x00', 24, 24 + STRING_LENGTH)].decode('UTF-8')

            #Ending of login server packet
            resp = b''
            resp += struct.pack('i', (0)) #Action code
            
            #Action codes:
            #0: Correct credentials
            #-1: An error occurred during logon
            #-2: Wrong credentials
            #-3: Already logged on
            #-4: Character does not belong to account
            #-5: Character on server and device
            #-6: Character not on server nor device

            resp += struct.pack('i', (1)) #Action code
            #Action codes:
            #0 = Already logged in
            #1 = Upload character (Advance state to 14)
            #2 = Start aworld (Advance state to 16)

            c.send(resp)

        elif packet_id == CLIENT_CHARACTER_UPLOAD_PACKET:
            if connection.stage != 2:
                c.close()
                return
            connection.stage = 3
            c.characterData = raw[8:]
            c.Character = Miuchiz.Character(c.characterData)
            c.Character.Info() #Display some information about handheld
            
            resp = b''
            resp += struct.pack('I', (SERVER_CHARACTER_UPLOAD_PACKET)) #Character upload packet id
            resp += b'\x10\x00\x00\x00' #Length
            resp += b'\x00\x00\x00\x00' #Action code
            resp += b'\x02\x00\x00\x00'
            #Action codes:
            #-6: Character not on server nor device
            #-5: Character on server and device
            #-4: Character does not belong to account
            #-3: Error occurred during character upload
            #-2: Error occurred during character upload
            #-1: Error occurred during character upload
            #0: Character not on server nor device
            
            c.send(resp)

        elif packet_id == CLIENT_REQUEST_CHARACTER_PACKET:
            if connection.stage != 3:
                c.close()
                return
            connection.stage = 4

            if not c.Character:
                c.close()
                return
            
            resp = b''
            resp += struct.pack('I', (SERVER_CHARACTER_UPDATE_PACKET))
            resp += struct.pack('I', (0x14 + len(c.characterData)))
            resp += b'\x00\x00\x00\x00'
            resp += b'\x00\x00\x00\x00'
            resp += b'\x01\x00\x00\x00'
            
##            Some things can be changed and saved if you want.
##            c.Character.creditz = 99999999
##            c.Character.happiness = 100
##            c.Character.hunger = 100
##            c.Character.boredom = 100
            d = c.Character.Output()
            resp += d
            
            c.send(resp)
            

        elif packet_id == CLIENT_GOODBYE_PACKET:
            c.close()
            return

connections = []        
def TestPacket():
    global connections
    c = connections[-1]
    resp = b''
    resp += struct.pack('I', (0x50001)) #Packet ID
    resp += b'\x35\x00\x00\x00' #Length
    resp += b'\x00\x00\x00\x00'
    resp += b'\x00\x00\x00\x00'
    resp += b'\x01\x00\x00\x00'
    resp += b'[Miuchiz Sync]\r\nVersion=1.0.0.67'
    resp += b'\x00'
    c.send(resp)

def Ping():
    global connections
    c = connections[-1]
    resp = b''
    resp += struct.pack('I', (SERVER_PING_PACKET)) #Packet ID
    resp += b'\x08\x00\x00\x00'
    c.send(resp)
            

def Listen(s):
    while True:
        s.listen(1)
        conn, addr = s.accept()
        print('Connected by', addr)
        connection = Connection(conn)
        Thread(target=HandleConnection, args = [connection]).start()
    
HOST = ''
PORT = 1492
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
Thread(target=Listen, args = [s]).start()
print('Hello.')
