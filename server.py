from sessions import *
from protocol import *
from authentication import *
from message import *
from location import *

 
factory = Factory()
factory.protocol = IphoneChat
factory.clients = []
reactor.listenTCP(80, factory)
print "Iphone Chat server started"
reactor.run()
