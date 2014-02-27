import struct
import copy
from sessions import *
from user import *

HEADER_LENGTH = 4
MAX_PACKET_SIZE = 5242880 #5 MB
TOKEN_LENGTH = 5

CMD_JOIN = 0
CMD_MSG = 1
CMD_TOKEN = 2
CMD_REAUTH = 3
CMD_REJOIN = 4
CMD_LOC = 5
CMD_MSG_CONFIRM = 6

ERR_SUCCESS = 0
ERR_WRONG_PASSWORD = 1
ERR_UNKNOWN_TOKEN = 2

class IphoneChat(Protocol):
    user = User() 
    packetLen = 0
    currentPacket = ''
    currentHeader = ''

    def connectionMade(self):
        self.factory.clients.append(self)
        print "clients are ", self.factory.clients
 
    def connectionLost(self, reason):
	    self.factory.clients.remove(self)

    def dataReceived(self, data):
        currentPos = [0]
        def readBytes(nBytes):
            bytes = data[currentPos[0]:currentPos[0]+nBytes]
            currentPos[0] += len(bytes)
            return bytes
        def hasDataLeft():
            return currentPos[0] < len(data)
        while hasDataLeft():
            if self.packetLen == 0:
                self.currentHeader += readBytes(HEADER_LENGTH - len(self.currentHeader))
                if len(self.currentHeader) < HEADER_LENGTH:
                    return
                self.packetLen = struct.unpack('<I', self.currentHeader)[0]
                self.currentHeader = ''
            if self.packetLen > MAX_PACKET_SIZE:
                print 'attack packet'
                self.transport.abortConnection()

            if self.packetLen > 0:
                self.currentPacket += readBytes(self.packetLen - len(self.currentPacket))
                if len(self.currentPacket) < self.packetLen:
                    return
                print 'received packet ', self.currentPacket
                self.processPacket(copy.copy(self.currentPacket))
                self.packetLen = 0
                self.currentPacket = ''
           
    def processPacket(self, packet):
        cmd = ord(packet[0])
        content = packet[1:]
        if (cmd in PROCESSOR_MAP):
            PROCESSOR_MAP[cmd](self,content)

    def sendPacket(self, packet):
        data = struct.pack('<I%ds' % (len(packet)), len(packet), packet)
        self.transport.write(data)

    def message(self, cmd, message):
        data = struct.pack('B%ds' % len(message), cmd, message)
        self.sendPacket(data)
