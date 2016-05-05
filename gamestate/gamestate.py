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
		self.bananaHalfWidth = 14  # based on banana-peel.png
		self.bananaHalfHeight = 9.5
		self.numBananas = 2
		self.isSlippingOnBanana = False
		self.lastBananaDropTime = time.clock()
		self.minDropInterval = 3 # number of seconds before you can drop another banana
		self.isDead = False

	# handle all keypresses
	# includes movement keys (arrow keys), collision handling, falling off the edge, dropping a banana
	# returns True/False if the keypress led to the player colliding with a banana
	def handleKeypresses(self, keys, player):
		isCollisionWithBanana = False
		# determine if p1 or p2 is currently moving
		if player == 'p1':
			opponent = self.gameState.p2_data
		elif player == 'p2':
			opponent = self.gameState.p1_data

		for key in keys:
			if self.isArrowKey(key):
				isCollisionWithBananaReturnVal = self.move(key, opponent)
				# only set isCollisionWithBanana flag to from False to True if there was a collision
				if isCollisionWithBananaReturnVal:
					isCollisionWithBanana = True
			elif key == pygame.K_SPACE and len(keys) > 1:
				self.dropBanana(key, keys)

		return isCollisionWithBanana

	# move player in the direction specified by the key
	# check for collisions with other players and with bananas on the stage
	# returns True/False if the keypress led to the player colliding with a banana
	def move(self, key, opponent):
		isCollisionWithBanana = False

		if key == pygame.K_RIGHT or key == pygame.K_LEFT:
			# set a direction specifier to indicate left vs right
			directionSpecifier = 1
			if key == pygame.K_LEFT:
				directionSpecifier = -1

			# move player
			self.xpos += directionSpecifier * self.moveLength

			if self.isCollision(opponent):
				# undo this player's movement and move the opponent instead
				self.xpos -= directionSpecifier * self.moveLength
				opponent.xpos += directionSpecifier * (self.moveLength + 1)
				opponent.checkFallOff()

		elif key == pygame.K_UP or key == pygame.K_DOWN:
			# set a direction specifier to indicate up (negative) vs down (positive)
			directionSpecifier = 1
			if key == pygame.K_UP:
				directionSpecifier = -1

			# move player
			self.ypos += directionSpecifier * self.moveLength
			if self.isCollision(opponent):
				# undo this player's movement and move the opponent instead
				self.ypos -= directionSpecifier * self.moveLength
				opponent.ypos += directionSpecifier * (self.moveLength + 1)
				opponent.checkFallOff()

		# check for collisions with bananas
		hitBanana = self.isCollisionWithBanana()
		if hitBanana != None:
			isCollisionWithBanana = True
			self.gameState.droppedBananas.remove(hitBanana)

		# check if player fell off after moving
		self.checkFallOff()

		return isCollisionWithBanana

	# if user didn't just drop a banana and they have bananas available, drop a banana behind the player
	# depending on the direction they are traveling
	def dropBanana(self, key, keys):
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

			# don't display banana if it is being dropped over the edge of the stage
			if self.isOffStage(bananaX, bananaY):
				return

			self.lastBananaDropTime = time.clock()
			self.numBananas -= 1
			self.gameState.droppedBananas.append({"xpos": bananaX, "ypos": bananaY})

	# check if the player has collided with any of the dropped bananas
	def isCollisionWithBanana(self):
		for banana in self.gameState.droppedBananas:
			bananaX = banana['xpos']
			bananaY = banana['ypos']
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
		if self.isOffStage(self.xpos, self.ypos):
			self.isDead = True

	# returns True/False if the given coordinates are off the edge of the board or not
	def isOffStage(self, x, y):
		if y < 100 or y > 500 or x< 200 or x> 600:
			return True
		else:
			return False

	def isArrowKey(self, key):
		if key == pygame.K_UP or key == pygame.K_DOWN or key == pygame.K_LEFT or key == pygame.K_RIGHT:
			return True
		else:
			return False

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
