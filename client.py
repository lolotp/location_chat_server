import socket
import struct

TCP_IP = 'memcap-chat.cloudapp.net'
TCP_PORT = 80
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP,TCP_PORT))

CMD_AUTH = 0

def sendMsg(msg):
    packet = struct.pack('<I%ds' % (len(msg)), len(msg),msg)
    s.send(packet)

def sendAuth():
    msg = str(chr(CMD_AUTH)) + struct.pack('<I',2) + '123456'
    sendMsg(msg)
