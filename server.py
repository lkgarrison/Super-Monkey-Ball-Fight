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
BANANA_RESPAWN_INTERVAL = 3
MAX_NUM_MOVEMENTS_AFTER_BANANA_COLLISION = 20
BANANA_SLIDE_INTERVAL = .1

# server's connection to player 1
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

		# signal to the game server that play can begin
		if self.gameServer.isReadyToStart():
			self.gameServer.sendStartSignal()

		self.gameServer.sendGameState()

	def dataReceived(self, data):
		# process any key presses
		# if player is currently slipping on banana, they don't get to move or place any more bananas
		if self.gameServer.gameState.p1_data.isSlippingOnBanana:
			return

		try:
			keys = pickle.loads(data)
			isCollisionWithBanana = self.gameServer.gameState.p1_data.handleKeypresses(keys, "p1")

			if isCollisionWithBanana:
				# remove space from set of keys because we only want to repeat the last movement keys
				collisionKeys = keys[:]
				if pygame.K_SPACE in collisionKeys:
					collisionKeys = keys.remove(pygame.K_SPACE)
				self.initBananaCollision(keys)
				self.movePlayerAfterBananaCollision()

		except Exception as ex:
			print ex
			pass

		self.gameServer.sendGameState()

	# initialize data that needs to be reset before moving player after each banana collision
	def initBananaCollision(self, keys):
		self.gameServer.gameState.p1_data.isSlippingOnBanana = True
		self.keysPressedUponCollision = keys
		self.numMovementsAfterBananaCollision = 0

	# function that forced the player who slid on the banana to keep sliding in the direction they were travelling X number of times
	def movePlayerAfterBananaCollision(self):
		if self.gameServer.gameState.p1_data.isDead is not True and self.numMovementsAfterBananaCollision < MAX_NUM_MOVEMENTS_AFTER_BANANA_COLLISION:
			self.numMovementsAfterBananaCollision += 1

			# simulate a keypress from the user (reuse the same logic that the server checks each time the user moves (falling off, etc))
			self.gameServer.gameState.p1_data.handleKeypresses(self.keysPressedUponCollision, "p1")
			self.gameServer.sendGameState()
			task.deferLater(reactor, BANANA_SLIDE_INTERVAL, self.movePlayerAfterBananaCollision)
		else:
			# allow player to move again
			self.gameServer.gameState.p1_data.isSlippingOnBanana = False
			self.gameServer.sendGameState()

	def connectionLost(self, reason):
		print "connection lost from", self.addr

class Player1CommandConnectionFactory(Factory):
	def __init__(self, gameServer):
		self.gameServer = gameServer

	def buildProtocol(self, addr):
		return Player1CommandConnection(addr, self.gameServer)


# server's connection to player 2
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
		# process any key presses
		# if player is currently slipping on banana, they don't get to move or place any more bananas
		if self.gameServer.gameState.p2_data.isSlippingOnBanana:
			return

		try:
			keys = pickle.loads(data)
			isCollisionWithBanana = self.gameServer.gameState.p2_data.handleKeypresses(keys, "p2")

			if isCollisionWithBanana:
				# remove space from set of keys because we only want to repeat the last movement keys
				collisionKeys = keys[:]
				if pygame.K_SPACE in collisionKeys:
					collisionKeys = keys.remove(pygame.K_SPACE)
				self.initBananaCollision(keys)
				self.movePlayerAfterBananaCollision()

		except Exception as ex:
			print ex
			pass

		self.gameServer.sendGameState()

	# initialize data that needs to be reset before moving player after each banana collision
	def initBananaCollision(self, keys):
		print "initialized banana collision"
		self.gameServer.gameState.p2_data.isSlippingOnBanana = True
		self.keysPressedUponCollision = keys
		self.numMovementsAfterBananaCollision = 0

	# function that forced the player who slid on the banana to keep sliding in the direction they were travelling X number of times
	def movePlayerAfterBananaCollision(self):
		if self.gameServer.gameState.p2_data.isDead is not True and self.numMovementsAfterBananaCollision < MAX_NUM_MOVEMENTS_AFTER_BANANA_COLLISION:
			self.numMovementsAfterBananaCollision += 1

			# simulate a keypress from the user (reuse the same logic that the server checks each time the user moves (falling off, etc))
			self.gameServer.gameState.p2_data.handleKeypresses(self.keysPressedUponCollision, "p2")
			self.gameServer.sendGameState()
			task.deferLater(reactor, BANANA_SLIDE_INTERVAL, self.movePlayerAfterBananaCollision)
		else:
			# allow player to move again
			self.gameServer.gameState.p2_data.isSlippingOnBanana = False
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
		self.p1_connection = None
		self.p2_connection = None

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
		task.deferLater(reactor, BANANA_RESPAWN_INTERVAL, self.incrementBananas)

	# increment the count of bananas for each player
	def incrementBananas(self):
		self.gameState.p1_data.numBananas += 1
		self.gameState.p2_data.numBananas += 1
		self.sendGameState()
		task.deferLater(reactor, BANANA_RESPAWN_INTERVAL, self.incrementBananas)

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

