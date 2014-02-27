from sessions import *
from protocol import *


def processMsg(chatProtocol, content):
    if chatProtocol.user.userId == 0:
        chatProtocol.message(CMD_REJOIN, '')
        return
    if len(content) < 5:
        return
    sequenceNumber = struct.unpack('<I', content[:4])[0]
    content = content[4:]
    msg = struct.pack('<I%ds' % (len(content)), chatProtocol.user.userId, content)
    for client in chatProtocol.factory.clients:
        print client
        if client == chatProtocol:
            print 'send confirm ', sequenceNumber
            client.message(CMD_MSG_CONFIRM,struct.pack('<I',sequenceNumber))
            continue
        c = client.user
        u = chatProtocol.user
        if (c.latitude != UNASSIGNED_DEGREE and c.longitude != UNASSIGNED_DEGREE and u.latitude != UNASSIGNED_DEGREE and u.longitude != UNASSIGNED_DEGREE):
            if (distance_on_unit_sphere(c.latitude, c.longitude, u.latitude, u.longitude) < 0.5):
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
