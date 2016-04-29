# Luke Garrison
# 4/28/2016
# work

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.defer import DeferredQueue

SERVER_ADDRESS = "student02.cse.nd.edu"
P1_PORT = 42201

class ServerCommandConnection(Protocol):
    def connectionMade(self):
        print "new connection made to", SERVER_ADDRESS, "port", P1_PORT
        
    def dataReceived(self, data):
        if data == "start data connection":
            reactor.connectTCP(SERVER_ADDRESS, DATA_PORT, HomeWorkDataConnectionFactory(self))
        return

    def dropDataConnection(self):
        # home.py is listening for this command. If it receives it, it will stop listening
        # on the data port
        self.transport.write("drop data connection")

    def connectionLost(self, reason):
        print "lost connection to", SERVER_ADDRESS, "port", P1_PORT


class ServerCommandConnectionFactory(ClientFactory):
    def buildProtocol(self, addr):
        return ServerCommandConnection()


if __name__ == "__main__":
    reactor.connectTCP(SERVER_ADDRESS, P1_PORT, ServerCommandConnectionFactory())

    reactor.run()
