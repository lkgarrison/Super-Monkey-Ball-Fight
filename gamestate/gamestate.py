import pygame
from pygame.locals import *

class PlayerData:
	def __init__(self, xpos=None, ypos=None, angle=None):
		self.xpos = xpos
		self.ypos = ypos
		self.angle = angle
		self.moveLength = 3

	def handleKeypress(self, key):
		if key == pygame.K_UP:
			self.ypos -= self.moveLength
		elif key == pygame.K_LEFT:
			self.xpos -= self.moveLength
		elif key == pygame.K_DOWN:
			self.ypos += self.moveLength
		elif key == pygame.K_RIGHT:
			self.xpos += self.moveLength

class GameState:
	def __init__(self):
		return

	def addPlayer1(self):
		p1_xpos = 225
		p1_ypos = 125
		initialAngle = 0
		self.p1_data = PlayerData(p1_xpos, p1_ypos, initialAngle)

	def addPlayer2(self):
		p2_xpos = 575
		p2_ypos = 475
		initialAngle = 0
		self.p2_data = PlayerData(p2_xpos, p2_ypos, initialAngle)
