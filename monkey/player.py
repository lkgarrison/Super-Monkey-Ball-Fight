# Nick Ward / Luke Garrison

import pygame

class Player(pygame.sprite.Sprite):
	def __init__(self, image, gs=None):
		self.image = image
		self.orig_image = self.image
		self.rect = self.image.get_rect()

	def update(self, data):
		self.angle = data.angle
		self.xpos = data.xpos
		self.ypos = data.ypos
		self.rect = self.image.get_rect()
		self.rect.center = (self.xpos, self.ypos)
