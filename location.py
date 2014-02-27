from sessions import *
from protocol import *

def processLoc(chatProtocol, content):
    if chatProtocol.user.userId == 0:
        chatProtocol.message(CMD_REJOIN, '')
        return
    strArray = content.split('|')
    if len(strArray) < 2:
        return
    try:
        latitude = float(strArray[0])
        longitude = float(strArray[1])
        chatProtocol.user.latitude = latitude
        chatProtocol.user.longitude = longitude
    except:
        print 'error converting coorindates'
registerProcessor(CMD_LOC, processLoc)
