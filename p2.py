# Luke Garrison, Nick Ward
# 4/29/2016
# p2

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.defer import DeferredQueue
from twisted.protocols.basic import LineReceiver
import pygame
from pygame.locals import *
import pickle
from monkey import *

SERVER_ADDRESS = "student02.cse.nd.edu"
P2_PORT = 42202
FPS = 30
TICK_RATE = 1.0 / FPS

class ServerCommandConnection(LineReceiver):
	def __init__(self):
		pygame.init()
		pygame.key.set_repeat(1, 50)  # repeats keyevents to support holding down keys
		self.windowSize = width, height = 800, 600
		self.screen = pygame.display.set_mode(self.windowSize)
		self.black = 0, 0, 0
		self.font = pygame.font.SysFont("monospace", 30)
		self.bananaImage = pygame.image.load('media/banana.png')
		self.bananaRect = self.bananaImage.get_rect()
		self.bananaRect.center = (720, 50)

		# inialize background
		self.backgroundImage = pygame.image.load('media/background.png')
		self.backgroundRect = self.backgroundImage.get_rect()
		self.backgroundRect.center = (400, 300)
		
		self.bothConnected = False
		p1Image = pygame.image.load('media/aiai.png')
		p2Image = pygame.image.load('media/gongon.png')
		self.players = [Player(p1Image), Player(p2Image)]
		reactor.callLater(TICK_RATE, self.tick)

	def connectionMade(self):
		print "new connection made to", SERVER_ADDRESS, "port", P2_PORT

	def lineReceived(self, data):
		if data == "start":
			print "both players are connected"
			self.bothConnected = True
		elif self.bothConnected:
			gamestate = pickle.loads(data)
			if gamestate.p1_data.isDead:
				print "Player 2 Wins!"
				reactor.stop()
			elif gamestate.p2_data.isDead:
				print "Player 1 Wins!"
				reactor.stop()
			self.players[0].update(gamestate.p1_data)
			self.players[1].update(gamestate.p2_data)
		else:
			try:
				gamestate = pickle.loads(data)
				self.players[1].update(gamestate.p2_data)
			except Exception as ex:
				print ex

	def connectionLost(self, reason):
		print "lost connection to", SERVER_ADDRESS, "port", P2_PORT

	# checks if keypress from pygame is an arrow key or not
	def isArrowKey(self, key):
		if key == pygame.K_UP or key == pygame.K_LEFT or key == pygame.K_DOWN or key == pygame.K_RIGHT:
			return True
		else:
			return False

	def tick(self):
		self.screen.fill(self.black)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				reactor.stop()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				reactor.stop()

			# only send events to allow movement to server if both players are connected
			if self.bothConnected:
				# handle arrow keys being pressed for movement
				if event.type == pygame.KEYDOWN:
					if self.isArrowKey(event.key):
						self.transport.write(str(event.key))

				# tell server that mouse was clicked
				if event.type == MOUSEBUTTONDOWN:
					# if left button was clicked
					if event.button == 1:
						self.transport.write("punch")

		# display background image
		self.screen.blit(self.backgroundImage, self.backgroundRect)

		# update players
		if self.bothConnected:
			for player in self.players:
				self.screen.blit(player.image, player.rect)
		else:
			# p1 is not connected yet, only display player 2
			self.screen.blit(self.players[1].image, self.players[1].rect)

		# display banana count
		label = self.font.render(str(self.players[0].numBananas), 1, (255,255,255))
		self.screen.blit(label, (755, 30))
		self.screen.blit(self.bananaImage, self.bananaRect)

		pygame.display.flip()
		reactor.callLater(TICK_RATE, self.tick)


class ServerCommandConnectionFactory(ClientFactory):
	def buildProtocol(self, addr):
		return ServerCommandConnection()

if __name__ == "__main__":
	reactor.connectTCP(SERVER_ADDRESS, P2_PORT, ServerCommandConnectionFactory())
	reactor.run()

