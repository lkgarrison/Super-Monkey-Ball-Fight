# Luke Garrison
# 4/29/2016
# game server

from twisted.internet.protocol import Factory, Protocol, ClientFactory
from twisted.internet.tcp import Port
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue

P1_PORT = 42201
P2_PORT = 42202

class Player1CommandConnection(Protocol):
    def __init__(self, addr, gameServer):
        # save addr for later use
        self.addr = addr
        self.gameServer = gameServer
        print "connection received from", addr

    def connectionMade(self):
        self.gameServer.p1_isConnected = True
        self.gameServer.getConnectionStatus()

    def dataReceived(self, data):
        print "command received from p1"

    def connectionLost(self, reason):
        print "connection lost from", self.addr

class Player1CommandConnectionFactory(Factory):
    def __init__(self, gameServer):
        self.gameServer = gameServer

    def buildProtocol(self, addr):
        return Player1CommandConnection(addr, self.gameServer)


class Player2CommandConnection(Protocol):
    def __init__(self, addr, gameServer):
        # save addr for later use
        self.addr = addr
        self.gameServer = gameServer
        print "connection received from", addr

    def connectionMade(self):
        self.gameServer.p2_isConnected = True
        self.gameServer.getConnectionStatus()

    def dataReceived(self, data):
        print "command received from p2"

    def connectionLost(self, reason):
        print "connection lost from", self.addr


class Player2CommandConnectionFactory(Factory):
    def __init__(self, gameServer):
        self.gameServer = gameServer

    def buildProtocol(self, addr):
        return Player1CommandConnection(addr, self.gameServer)


class GameServer():
    def __init__(self):
        reactor.listenTCP(P1_PORT, Player1CommandConnectionFactory(self))
        reactor.listenTCP(P2_PORT, Player2CommandConnectionFactory(self))

        self.p1_isConnected = False;
        self.p2_isConnected = False;

    def getConnectionStatus(self):
        if self.p1_isConnected and self.p2_isConnected:
            print "Both players are connected"
        elif self.p1_isConnected and not self.p2_isConnected:
            print "p1 is connected, but p2 is not"
        elif not self.p1_isConnected and self.p2_isConnected:
            print "p2 is connected, but p1 is not"
        else:
            print "Neither player is connected"
    
    # returns True/False if both players are connected to the game server
    def isReadyToStart(self):
        if self.p1_isConnected and self.p2_isConnected:
            return True
        else:
            return False


if __name__ == "__main__":
    sever = GameServer()
    reactor.run()
