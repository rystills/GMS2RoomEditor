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
		self.pressPos = (0,0)
		self.followMouse = False
		self.pressed = False
		
	def update(self):
		#if we are in follow mouse mode, don't do anything until we detect a leftclick
		if (self.followMouse):
			self.rect.center = pygame.mouse.get_pos()
			#exit follow mode when mouse is pressed	
			if (GM.mousePressedLeft):
				self.followMouse = False
			return
		#check mouse button status
		#check if mouse is on this button 
		self.state = "neutral"
		if (self.rect.collidepoint(pygame.mouse.get_pos())):
			#if mouse button was just pressed on us, toggle pressed on
			if (GM.mousePressedLeft): 
				self.pressed = True
				self.pressPos = pygame.mouse.get_pos()
			
			#if mouse button was just released on us, trigger a press 
			if (GM.mouseReleasedLeft and self.pressed):
				pass
				#self.function(*self.args)
			
			#set state based off of pressed
			self.state = "press" if self.pressed else "hover"
		
		#if mouse button is not held down, toggle pressed off
		if (not GM.mouseDownLeft): 
			self.pressed = False
			
		#if pressed, move with mouse
		if (self.pressed):
			mousePos = pygame.mouse.get_pos()
			posDiff = (mousePos[0]-self.pressPos[0],mousePos[1]-self.pressPos[1])
			self.x += posDiff[0]
			self.y += posDiff[1]
			self.rect.centerx = self.x
			self.rect.centery = self.y
			self.pressPos = mousePos