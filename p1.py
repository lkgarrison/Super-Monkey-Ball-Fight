# Luke Garrison, Nick Ward
# 4/29/2016
# p1

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.defer import DeferredQueue

SERVER_ADDRESS = "student02.cse.nd.edu"
P1_PORT = 42201

class ServerCommandConnection(Protocol):
    def connectionMade(self):
        print "new connection made to", SERVER_ADDRESS, "port", P1_PORT
        
    def dataReceived(self, data):
        print data

    def connectionLost(self, reason):
        print "lost connection to", SERVER_ADDRESS, "port", P1_PORT


class ServerCommandConnectionFactory(ClientFactory):
    def buildProtocol(self, addr):
        return ServerCommandConnection()


if __name__ == "__main__":
    reactor.connectTCP(SERVER_ADDRESS, P1_PORT, ServerCommandConnectionFactory())

    reactor.run()
