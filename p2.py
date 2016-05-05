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

		# set up default graphics window
		self.windowSize = windowWidth, windowHeight = 800, 600
		self.screen = pygame.display.set_mode(self.windowSize)
		self.black = 0, 0, 0
		self.gamestate = None
		self.font = pygame.font.SysFont("monospace", 30)
		self.bananaImage = pygame.image.load('media/banana.png')
		self.bananaRect = self.bananaImage.get_rect()
		self.bananaRect.center = (720, 50)

		# initialize bananas
		self.font = pygame.font.SysFont("monospace", 30)
		self.bananaImage = pygame.image.load('media/banana.png')
		self.bananaRect = self.bananaImage.get_rect()
		self.bananaRect.center = (720, 50)

		self.bananaPeelImage = pygame.image.load('media/banana-peel.png')
		self.bananaPeelRect = self.bananaPeelImage.get_rect()

		self.bananaPeelRottenImage = pygame.image.load('media/banana-peel-rotten.png')
		self.bananaPeelRottenRect = self.bananaPeelRottenImage.get_rect()

		# initialize slipping on banana warning sign
		self.slipWarningSignImage = pygame.image.load('media/banana-warning-sign.png')
		self.slipWarningSignRect = self.slipWarningSignImage.get_rect()
		self.slipWarningSignRect.center = (windowWidth/2, 50)

		# initialize "waiting for other player" text
		self.waitingForOpponentLabel = self.font.render("Waiting for Opponent to join...", 1, (255,255,255))
		self.waitingForOpponentLabelPos = (windowWidth/2 - self.waitingForOpponentLabel.get_width()/2, windowHeight/2 - self.waitingForOpponentLabel.get_height()/2)

		# initialize stage
		self.stageImage = pygame.image.load('media/stage.png')
		self.stageRect = self.stageImage.get_rect()
		self.stageRect.center = (windowWidth/2, windowHeight/2)

		# inialize background
		self.backgroundImage = pygame.image.load('media/background.png')
		self.backgroundImage = pygame.transform.scale(self.backgroundImage, self.windowSize)
		self.backgroundRect = self.backgroundImage.get_rect()
		self.backgroundRect.center = (windowWidth/2, windowHeight/2)
		
		self.bothConnected = False	# prevents game form starting until both players are connected

		# load and initialize players
		p1Image = pygame.image.load('media/aiai.png')
		p2Image = pygame.image.load('media/gongon.png')
		self.players = [Player(p1Image), Player(p2Image)]

		# updates the gamestate
		reactor.callLater(TICK_RATE, self.tick)

	def connectionMade(self):
		print "new connection made to", SERVER_ADDRESS, "port", P2_PORT

	def lineReceived(self, data):
		if data == "start":
			print "both players are connected"
			self.bothConnected = True
		elif self.bothConnected:
			# check if either player was knocked off
			self.gamestate = pickle.loads(data)
			if self.gamestate.p1_data.isDead:
				print "Player 2 Wins!"
				reactor.stop()
			elif self.gamestate.p2_data.isDead:
				print "Player 1 Wins!"
				reactor.stop()
			self.players[0].update(self.gamestate.p1_data)
			self.players[1].update(self.gamestate.p2_data)

		else:
			# set initial position of player 2
			try:
				self.gamestate = pickle.loads(data)
				self.players[1].update(self.gamestate.p2_data)
			except Exception as ex:
				print ex

	def connectionLost(self, reason):
		print "lost connection to", SERVER_ADDRESS, "port", P2_PORT

	# get a list of the keys that are pressed that we want to handle
	def addValidKeys(self, possibleKeys):
		# valid keys to handle actions for
		validKeys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE]
		pressedValidKeys = list()

		for key in validKeys:
			if possibleKeys[key] == 1:
				pressedValidKeys.append(key)

		return pressedValidKeys

	# main loop that is called each FPS to process the players events and send them to the server
	# update's players display
	def tick(self):
		self.screen.fill(self.black)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				reactor.stop()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				reactor.stop()

		# only send events to allow movement to server if both players are connected
		if self.bothConnected:
			validKeys = self.addValidKeys(pygame.key.get_pressed())
			if len(validKeys) is not 0:
				self.transport.write(pickle.dumps(validKeys))

		# display background and stage images
		self.screen.blit(self.backgroundImage, self.backgroundRect)
		self.screen.blit(self.stageImage, self.stageRect)

		# display "waiting for other players to join" message if not all players have joined
		if not self.bothConnected:
			self.screen.blit(self.waitingForOpponentLabel, self.waitingForOpponentLabelPos)

		# update players
		if self.bothConnected:
			for player in self.players:
				self.screen.blit(player.image, player.rect)
		else:
			# p1 is not connected yet, only display player 2
			self.screen.blit(self.players[1].image, self.players[1].rect)

		# display dropped bananas
		if hasattr(self.gamestate, 'droppedBananas'):
			for banana in self.gamestate.droppedBananas:
				# display rotten vs regular banana peel
				if banana['isRotten']:
					self.bananaPeelRottenRect.center = (banana['xpos'], banana['ypos'])
					self.screen.blit(self.bananaPeelRottenImage, self.bananaPeelRottenRect)
				else:
					self.bananaPeelRect.center = (banana['xpos'], banana['ypos'])
					self.screen.blit(self.bananaPeelImage, self.bananaPeelRect)

		# display banana count
		if hasattr(self.players[1], 'numBananas'):
			label = self.font.render(str(self.players[1].numBananas), 1, (255,255,255))
			self.screen.blit(label, (755, 30))
			self.screen.blit(self.bananaImage, self.bananaRect)

		# display slip warning sign if player is currently slipping
		if self.players[1].isSlippingOnBanana:
			self.screen.blit(self.slipWarningSignImage, self.slipWarningSignRect)

		pygame.display.flip()
		reactor.callLater(TICK_RATE, self.tick)


class ServerCommandConnectionFactory(ClientFactory):
	def buildProtocol(self, addr):
		return ServerCommandConnection()

if __name__ == "__main__":
	reactor.connectTCP(SERVER_ADDRESS, P2_PORT, ServerCommandConnectionFactory())
	reactor.run()

