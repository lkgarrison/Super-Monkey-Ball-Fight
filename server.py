# Luke Garrison, Nick Ward
# 4/29/2016
# game server

from twisted.internet.protocol import Factory, Protocol, ClientFactory
from twisted.internet.tcp import Port
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from twisted.internet import task
from gamestate import *
import pickle

P1_PORT = 42201
P2_PORT = 42202
BANANA_INTERVAL = 3

class Player1CommandConnection(Protocol):
	def __init__(self, addr, gameServer):
		self.addr = addr
		self.gameServer = gameServer
		self.gameServer.p1_connection = self
		print "connection received from", addr
		print "p1 is connected"

	def connectionMade(self):
		self.gameServer.gameState.addPlayer1()
		self.gameServer.p1_isConnected = True
		if self.gameServer.isReadyToStart():
			self.gameServer.sendStartSignal()

		self.gameServer.sendGameState()

	def dataReceived(self, data):
		#process data
		try:
			key = int(data)
			self.gameServer.gameState.p1_data.handleKeypress(key, "p1")
		except Exception as ex:
			pass

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
		self.gameServer.gameState.addPlayer2()
		self.gameServer.p2_isConnected = True
		if self.gameServer.isReadyToStart():
			self.gameServer.sendStartSignal()

		self.gameServer.sendGameState()


	def dataReceived(self, data):
		#process data
		try:
			key = int(data)
			self.gameServer.gameState.p2_data.handleKeypress(key, "p2")
		except Exception as ex:
			pass

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
		print "sending start signal"
		self.p1_connection.transport.write("start\r\n")
		self.p2_connection.transport.write("start\r\n")

		# start giving bananas to each player
		task.deferLater(reactor, BANANA_INTERVAL, self.incrementBananas)

	# increment the count of bananas for each player
	def incrementBananas(self):
		self.gameState.p1_data.numBananas += 1
		self.gameState.p2_data.numBananas += 1
		self.sendGameState()
		task.deferLater(reactor, BANANA_INTERVAL, self.incrementBananas)

	# send game state to all connected players
	def sendGameState(self):
		gameStateString = pickle.dumps(self.gameState)
		try:
			self.p1_connection.transport.write(gameStateString + "\r\n")
 		except:
 			pass

 		try:
 			self.p2_connection.transport.write(gameStateString + "\r\n")
 		except:
 			pass

if __name__ == "__main__":
	sever = GameServer()
	reactor.run()

