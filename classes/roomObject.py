'''
Created on Jul 28, 2017

@author: Ryan
'''
import pygame
import GM

#class that represents an object present in the curretly selected room
class RoomObject(pygame.sprite.Sprite):
	def __init__(self,x,y,objType,rot=0,scale=1):
		self.x = x
		self.y = y
		self.objType = objType
		self.rot = rot
		self.scale = scale