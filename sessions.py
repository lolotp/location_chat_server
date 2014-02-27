from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.enterprise import adbapi

PROCESSOR_MAP = {}
STORED_SESSIONS = {}

def registerProcessor(command, func):
    PROCESSOR_MAP[command] = func
