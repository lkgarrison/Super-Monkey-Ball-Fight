# Nick Ward, Luke Garrison

import pygame
from pygame.locals import *
from twisted.internet import reactor
from twisted.internet import task
import time
import math
import pickle

class PlayerData:
	def __init__(self, gameState, xpos=None, ypos=None):
		self.xpos = xpos
		self.ypos = ypos
		self.moveLength = 4
		self.gameState = gameState
		self.radius = 17 # radius of ball based on image
		self.bananaHalfWidth = 14
		self.bananaHalfHeight = 9.5
		self.numBananas = 0
		self.isSlippingOnBanana = False
		self.isDead = False
		self.lastBananaDropTime = time.clock()
		self.minDropInterval = 3 # number of seconds before you can drop another banana

	# handle all keypresses
	# includes movement keys (arrow keys), collision handling, falling off the edge, dropping a banana
	# returns True/False if the keypress led to the player colliding with a banana
	def handleKeypresses(self, keys, player):
		isCollisionWithBanana = False
		for key in keys:
			# determine if p1 or p2 is currently moving
			if player == 'p1':
				opponent = self.gameState.p2_data
			elif player == 'p2':
				opponent = self.gameState.p1_data

			if key == pygame.K_UP:
				self.ypos -= self.moveLength
				hitBanana = self.isCollisionWithBanana()
				if hitBanana != None:
					print player, "hit a banana!"
					isCollisionWithBanana = True
					self.gameState.droppedBananas.remove(hitBanana)
				if self.isCollision(opponent):
					# undo this player's movement and move the opponent instead
					self.ypos += self.moveLength
					opponent.ypos -= (self.moveLength + 1)
					opponent.checkFallOff()
				self.checkFallOff()
			elif key == pygame.K_LEFT:
				self.xpos -= self.moveLength
				hitBanana = self.isCollisionWithBanana()
				if hitBanana != None:
					print player, "hit a banana!"
					isCollisionWithBanana = True
					self.gameState.droppedBananas.remove(hitBanana)
				if self.isCollision(opponent):
					# undo this player's movement and move the opponent instead
					self.xpos += self.moveLength
					opponent.xpos -= (self.moveLength + 1)
					opponent.checkFallOff()
				self.checkFallOff()
			elif key == pygame.K_DOWN:
				self.ypos += self.moveLength
				hitBanana = self.isCollisionWithBanana()
				if hitBanana != None:
					print player, "hit a banana!"
					isCollisionWithBanana = True
					self.gameState.droppedBananas.remove(hitBanana)
				if self.isCollision(opponent):
					# undo this player's movement and move the opponent instead
					self.ypos -= self.moveLength
					opponent.ypos += (self.moveLength + 1)
					opponent.checkFallOff()
				self.checkFallOff()
			elif key == pygame.K_RIGHT:
				self.xpos += self.moveLength
				hitBanana = self.isCollisionWithBanana()
				if hitBanana != None:
					print player, "hit a banana!"
					isCollisionWithBanana = True
					self.gameState.droppedBananas.remove(hitBanana)
				if self.isCollision(opponent):
					# undo this player's movement and move the opponent instead
					self.xpos -= self.moveLength
					opponent.xpos += (self.moveLength + 1)
					opponent.checkFallOff()
				self.checkFallOff()

			# if user pressed space while moving
			elif key == pygame.K_SPACE and len(keys) > 1:
				# if user has bananas to drop and it has been minDropInterval, player can drop the banana
				if self.numBananas > 0 and (time.clock() - self.lastBananaDropTime) * 1000 >= self.minDropInterval:
					# drop a banana
					bananaX = self.xpos
					bananaY = self.ypos
					
					# place the banana behind the user the amount of self.radius
					# find out which other keys were pressed
					movementKeys = keys[:] # make a copy of the original list of keys
					movementKeys.remove(key) # remove space key from list of keys
					for mk in movementKeys:
						if mk == pygame.K_UP:
							bananaY += 2*self.radius
						if mk == pygame.K_DOWN:
							bananaY -= 2*self.radius
						if mk == pygame.K_RIGHT:
							bananaX -= 2*self.radius
						if mk == pygame.K_LEFT:
							bananaX += 2*self.radius

					self.lastBananaDropTime = time.clock()
					self.numBananas -= 1
					self.gameState.droppedBananas.append({"x": bananaX, "y": bananaY})

		return isCollisionWithBanana
	
	# check if the player has collided with any of the dropped bananas
	def isCollisionWithBanana(self):
		for banana in self.gameState.droppedBananas:
			bananaX = banana['x']
			bananaY = banana['y']
			dx = self.xpos - bananaX
			dy = self.ypos - bananaY
			radiusSum = self.radius + math.sqrt((self.bananaHalfWidth**2) + (self.bananaHalfHeight**2))

			# is collision
			if ((dx * dx) + (dy * dy)) < (radiusSum * radiusSum):
				return banana

		# no collisions with bananas
		return None

	# checks if the players have collided
	def isCollision(self, opponent):
		dx = self.xpos - opponent.xpos
		dy = self.ypos - opponent.ypos
		radiusSum = self.radius + opponent.radius
		if ((dx * dx) + (dy * dy)) < (radiusSum * radiusSum):
			return True
		else:
			return False

	# check if the player has fallen off the board (center of character is off the grid)
	# if true, sets player's isDead property, which clients check for
	def checkFallOff(self):
		if self.ypos < 100 or self.ypos > 500 or self.xpos < 200 or self.xpos > 600:
			self.isDead = True

class GameState:
	def __init__(self):
		self.droppedBananas = list()

	def addPlayer1(self):
		p1_xpos = 225
		p1_ypos = 125
		self.p1_data = PlayerData(self, p1_xpos, p1_ypos)

	def addPlayer2(self):
		p2_xpos = 575
		p2_ypos = 475
		self.p2_data = PlayerData(self, p2_xpos, p2_ypos)
