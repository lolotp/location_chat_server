from sessions import *
from protocol import *
import location

def processMsg(chatProtocol, content):
    if chatProtocol.user.userId == 0:
        chatProtocol.message(CMD_REJOIN, '')
        return
    if len(content) < 5:
        return
    sequenceNumber = struct.unpack('<I', content[:4])[0]
    content = content[4:]
    msg = struct.pack('<I%ds' % (len(content)), chatProtocol.user.userId, content)
    print 'send confirm ', sequenceNumber
    chatProtocol.message(CMD_MSG_CONFIRM,struct.pack('<I',sequenceNumber))
    for client in location.getNearbyClients(chatProtocol.factory.clients, chatProtocol):
      client.message(CMD_MSG, msg)

registerProcessor(CMD_MSG, processMsg)

def processToken(chatProtocol, content):
    strArray = content.split('|')
    if len(strArray) < 1:
        chatProtocol.message(CMD_REAUTH,str(chr(ERR_UNKNOWN_TOKEN)))
    token = strArray[0]
    if token in STORED_SESSIONS:
        chatProtocol.user = STORED_SESSIONS[token]
        if len(strArray) > 2:
            original_lat = chatProtocol.user.latitude
            original_long = chatProtocol.user.longitude
            try:
                chatProtocol.user.latitude = float(strArray[1])
                chatProtocol.user.longitude = float(strArray[2])
            except:
                chatProtocol.user.latitude = original_lat
                chatProtocol.user.longitude = original_long
    else:
        chatProtocol.message(CMD_REJOIN,'')
registerProcessor(CMD_TOKEN, processToken)
