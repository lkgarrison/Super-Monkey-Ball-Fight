import pygame
from pygame.locals import *

class PlayerData:
	def __init__(self, gs, xpos=None, ypos=None, angle=None):
		self.xpos = xpos
		self.ypos = ypos
		self.angle = angle
		self.moveLength = 4
		self.gameState = gs
		self.radius = 17 # radius of ball based on image
		self.numBananas = 0
		self.isDead = False

	def handleKeypress(self, key, player):
		# determine if p1 or p2 is currently moving
		if player == 'p1':
			opponent = self.gameState.p2_data
		elif player == 'p2':
			opponent = self.gameState.p1_data

		if key == pygame.K_UP:
			self.ypos -= self.moveLength
			if self.isCollision(opponent):
				# undo this player's movement and move the opponent instead
				self.ypos += self.moveLength
				opponent.ypos -= (self.moveLength + 1)
				opponent.checkFallOff()
			self.checkFallOff()
		elif key == pygame.K_LEFT:
			self.xpos -= self.moveLength
			if self.isCollision(opponent):
				# undo this player's movement and move the opponent instead
				self.xpos += self.moveLength
				opponent.xpos -= (self.moveLength + 1)
				opponent.checkFallOff()
			self.checkFallOff()
		elif key == pygame.K_DOWN:
			self.ypos += self.moveLength
			if self.isCollision(opponent):
				# undo this player's movement and move the opponent instead
				self.ypos -= self.moveLength
				opponent.ypos += (self.moveLength + 1)
				opponent.checkFallOff()
			self.checkFallOff()
		elif key == pygame.K_RIGHT:
			self.xpos += self.moveLength
			if self.isCollision(opponent):
				# undo this player's movement and move the opponent instead
				self.xpos -= self.moveLength
				opponent.xpos += (self.moveLength + 1)
				opponent.checkFallOff()
			self.checkFallOff()
		elif key == pygame.K_SPACE:
			# drop a banana
			print "banana dropped!"
			self.gameState.droppedBananas.append({"x": self.xpos, "y": self.ypos})
			print "number of bananas dropped:", str(len(self.gameState.droppedBananas))

	# checks if the players have collided
	def isCollision(self, opponent):
		dx = self.xpos - opponent.xpos
		dy = self.ypos - opponent.ypos
		radiusSum = self.radius + opponent.radius
		if ((dx * dx) + (dy * dy)) < (radiusSum * radiusSum):
			return True
		else:
			return False

	def checkFallOff(self):
		if self.ypos < 100 or self.ypos > 500 or self.xpos < 200 or self.xpos > 600:
			self.isDead = True
			raise Exception('fall')
		else:
			return

class GameState:
	def __init__(self):
		self.droppedBananas = list()

	def addPlayer1(self):
		p1_xpos = 225
		p1_ypos = 125
		initialAngle = 0
		self.p1_data = PlayerData(self, p1_xpos, p1_ypos, initialAngle)

	def addPlayer2(self):
		p2_xpos = 575
		p2_ypos = 475
		initialAngle = 0
		self.p2_data = PlayerData(self, p2_xpos, p2_ypos, initialAngle)
