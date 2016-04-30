# Luke Garrison, Nick Ward
# 4/29/2016
# game server

from twisted.internet.protocol import Factory, Protocol, ClientFactory
from twisted.internet.tcp import Port
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from gamestate import *
import pickle

P1_PORT = 42201
P2_PORT = 42202

class Player1CommandConnection(Protocol):
    def __init__(self, addr, gameServer):
        self.addr = addr
        self.gameServer = gameServer
        self.gameServer.p1_connection = self
        print "connection received from", addr
        print "p1 is connected"

    def connectionMade(self):
        self.gameServer.p1_isConnected = True
        if self.gameServer.isReadyToStart():
            self.gameServer.sendStartSignal()

    def dataReceived(self, data):
        print "command received from p1"
        print data

        #process data
        self.gameServer.sendGameState()

    def connectionLost(self, reason):
        print "connection lost from", self.addr

class Player1CommandConnectionFactory(Factory):
    def __init__(self, gameServer):
        self.gameServer = gameServer

    def buildProtocol(self, addr):
        return Player1CommandConnection(addr, self.gameServer)


class Player2CommandConnection(Protocol):
    def __init__(self, addr, gameServer):
        self.addr = addr
        self.gameServer = gameServer
        print "connection received from", addr
        print "p2 is connected"
        self.gameServer.p2_connection = self

    def connectionMade(self):
        self.gameServer.p2_isConnected = True
        if self.gameServer.isReadyToStart():
            self.gameServer.sendStartSignal()

    def dataReceived(self, data):
        print "command received from p2"
        print data

        #process data
        self.gameServer.sendGameState()

    def connectionLost(self, reason):
        print "connection lost from", self.addr


class Player2CommandConnectionFactory(Factory):
    def __init__(self, gameServer):
        self.gameServer = gameServer

    def buildProtocol(self, addr):
        return Player2CommandConnection(addr, self.gameServer)


class GameServer():
    def __init__(self):
        reactor.listenTCP(P1_PORT, Player1CommandConnectionFactory(self))
        reactor.listenTCP(P2_PORT, Player2CommandConnectionFactory(self))

        self.p1_isConnected = False;
        self.p2_isConnected = False;

        self.gameState = GameState()

    # returns True/False if both players are connected to the game server
    def isReadyToStart(self):
        if self.p1_isConnected and self.p2_isConnected:
            return True
        else:
            return False

    def sendStartSignal(self):
        self.p1_connection.transport.write("start")
        self.p2_connection.transport.write("start")

    # send game state to all connected players
    def sendGameState(self):
        gameStateString = pickle.dumps(self.gameState)
        if self.p1_connection is not None:
            self.p1_connection.transport.write(gameStateString)
        if self.p2_connection is not None:
            self.p2_connection.transport.write(gameStateString)

if __name__ == "__main__":
    sever = GameServer()
    reactor.run()

