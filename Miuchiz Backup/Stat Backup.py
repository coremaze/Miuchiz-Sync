import socket
import Miuchiz
from PACKET_IDS import *
from threading import Thread
import struct
import time
import sys
class Connection():
    def __init__(self, conn):
        self.conn = conn
        self.Character = None
    def recv(self, b):
        return self.conn.recv(b)
    def send(self, b):
        return self.conn.send(b)
    def close(self):
        return self.conn.close()
def stripQuotes(s):
    out = s
    if out.startswith('"') and out.endswith('"'):
        out = out[1:-1]
    return out
if len(sys.argv) != 3:
    print('USAGE: %s < backup | restore > <Backup file>' % sys.argv[0].split('\\')[-1])
    exit()
    
if sys.argv[1].lower() == 'backup':
    backup = True
elif sys.argv[1].lower() == 'restore':
    backup = False
else:
    print('Invalid setting: "%s"' % sys.argv[1])
    exit()
    
filename = stripQuotes(sys.argv[2])

HOST = ''
PORT = 1492
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print('Waiting for a connection from Miuchiz Sync...')
conn, addr = s.accept()
print('Connection accepted.')
connection = Connection(conn)
c = connection
while conn:
    try: raw = c.recv(8192)
    except: break
    if not raw: break
    formatted_data =  "".join("%02x " % b for b in raw)
    packet_id = struct.unpack('I', raw[0:4])[0]
    
    if packet_id == CLIENT_INITIAL_PACKET:
        print('Communication has started.')

        #Welcome packet
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
        STRING_LENGTH = 16
        username = raw[8 : raw.find(b'\x00', 8, 8 + STRING_LENGTH)].decode('UTF-8')
        password = raw[24 : raw.find(b'\x00', 24, 24 + STRING_LENGTH)].decode('UTF-8')

        #Ending of login server packet
        resp = b''
        resp += struct.pack('i', (0)) #Action code 0: Correct credentials
        resp += struct.pack('i', (1)) #Action code 1: Upload character

        c.send(resp)

    elif packet_id == CLIENT_CHARACTER_UPLOAD_PACKET:
        c.Character = Miuchiz.Character(raw[8:])
        c.Character.Info() #Display some information about handheld
        if backup:
            with open(filename, 'wb') as file:
                print('Saving character to %s' % filename)
                file.write(c.Character.char_data)
        
        resp = b''
        resp += struct.pack('I', (SERVER_CHARACTER_UPLOAD_PACKET)) #Character upload packet id
        resp += b'\x10\x00\x00\x00' #Length
        resp += b'\x00\x00\x00\x00' 
        resp += b'\x02\x00\x00\x00'

        c.send(resp)

        #Log the client off with a custom packet
        time.sleep(2)
        print('Disconnecting handheld from server...')
        resp = b''
        resp += struct.pack('I', (0x10002)) #Packet ID
        resp += b'\x08\x00\x00\x00' #Length
        c.send(resp)

    elif packet_id == CLIENT_REQUEST_CHARACTER_PACKET:
        if not backup:
            with open(filename, 'rb') as file:
                print('Restoring backup data to handheld...')
                d = file.read()
        else:
            d = c.Character.Output()
        resp = b''
        resp += struct.pack('I', (SERVER_CHARACTER_UPDATE_PACKET))
        resp += struct.pack('I', (0x14 + len(c.Character.char_data)))
        resp += b'\x00\x00\x00\x00'
        resp += b'\x00\x00\x00\x00'
        resp += b'\x01\x00\x00\x00'
        resp += d
        
        c.send(resp)
        
try:
    c.close()
except:
    pass
print('Communication has ended.')
