'''
Created on Jul 28, 2017

@author: Ryan
'''
import pygame
import GM
from util import *

#class that represents an object present in the curretly selected room
class RoomObject(pygame.sprite.Sprite):
	def __init__(self,x,y,objType,rot=0,scale=1):
		pygame.sprite.Sprite.__init__(self)
		#store basic properties about the object we represent in the ecurrent room
		self.x = x
		self.y = y
		self.objType = objType
		self.rot = rot
		self.scale = scale
		self.image = loadObjectSprite(self.objType)
		self.rect = self.image.get_rect()
		self.layer = None
		#move our image to be centered at our x,y pos
		self.rect.centerx = self.x
		self.rect.centery = self.y