import pygame
from pygame.locals import *

class PlayerData:
	def __init__(self, gs, xpos=None, ypos=None, angle=None):
		self.xpos = xpos
		self.ypos = ypos
		self.angle = angle
		self.moveLength = 3
		self.gameState = gs
		self.isDead = False

	def handleKeypress(self, key):
		if key == pygame.K_UP:
			self.ypos -= self.moveLength
			self.checkFallOff()
		elif key == pygame.K_LEFT:
			self.xpos -= self.moveLength
			self.checkFallOff()
		elif key == pygame.K_DOWN:
			self.ypos += self.moveLength
			self.checkFallOff()
		elif key == pygame.K_RIGHT:
			self.xpos += self.moveLength
			self.checkFallOff()

	def checkFallOff(self):
		if self.ypos < 100 or self.ypos > 500 or self.xpos < 200 or self.xpos > 600:
			self.isDead = True
			raise Exception('fall')
		else:
			return

class GameState:
	def __init__(self):
		return

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
