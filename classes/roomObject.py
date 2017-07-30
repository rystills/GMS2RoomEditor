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
		self.noSnapRot = self.rot
		self.scale = scale
		self.noSnapScale = self.scale
		self.baseImage,self.imgHasAlpha = loadObjectSprite(self.objType)
		self.image = self.baseImage.copy()
		self.rect = self.image.get_rect()
		self.layer = None
		#move our image to be centered at our x,y pos
		self.rect.centerx = self.x
		self.rect.centery = self.y
		self.followMouse = False
		self.pressed = False
		print(self.imgHasAlpha)
		
	#set rotation to specified rot value
	def setRotation(self,newRot):
		self.noSnapRot = newRot % 360
		roundRot = roundBase(self.noSnapRot) % 360 if GM.angleSnaps else self.noSnapRot
		#do nothing if new rotation is the same as old rotation
		if (roundRot != self.rot):
			self.rot = roundRot
			#don't bother rotating the base image if our new rotation is 0
			self.image = pygame.transform.rotate(self.baseImage,roundRot) if roundRot != 0 else self.baseImage.copy()
			#convert with alpha
			if (self.imgHasAlpha):
				self.image = self.image.convert_alpha()
			#convert without alpha
			else:
				self.image = self.image.convert()
			#update rect to rotated image, preserving old rect center
			self.rect = self.image.get_rect()
			self.rect.centerx = self.x
			self.rect.centery = self.y
			
	def setScale(self,newScale):
		print("old scale: " + str(self.scale))
		print("new scale: " + str(newScale))
		self.noSnapScale = max(newScale,0.05)
		roundScale = roundBase(self.noSnapScale,0.05,2) if GM.scaleSnaps else self.noSnapScale
		#do nothing if new rotation is the same as old rotation
		if (roundScale != self.scale):
			self.scale = roundScale
			#don't bother rotating the base image if our new rotation is 0
			self.image = pygame.transform.scale(self.baseImage,
											(int(self.baseImage.get_width()*roundScale),int(self.baseImage.get_height()*roundScale))) if roundScale != 1 else self.baseImage.copy()
			#convert with alpha
			if (self.imgHasAlpha):
				self.image = self.image.convert_alpha()
			#convert without alpha
			else:
				self.image = self.image.convert()
			#update rect to rotated image, preserving old rect center
			self.rect = self.image.get_rect()
			self.rect.centerx = self.x
			self.rect.centery = self.y
		
	def update(self):
		#if we are in follow mouse mode, don't do anything until we detect a leftclick
		if (self.followMouse):
			self.rect.center = GM.mouseX,GM.mouseY
			#exit follow mode when mouse is pressed	
			if (GM.mousePressedLeft):
				self.followMouse = False
				#once we finish dragging, update x,y pos to rect pos
				self.x = self.rect.centerx
				self.y = self.rect.centery
				#set selection to this object, now that we've placed it
				GM.selection = self
				GM.selectedThisPress = True
				GM.placingObject = False
			return
		
		#don't do standard object update is we are in the process of placing an object
		if (GM.placingObject):
			return
		#check mouse button status
		#check if mouse is on this button 
		self.state = "neutral"
		if (self.rect.collidepoint(GM.mouseX,GM.mouseY)):
			#if mouse button was just pressed on us, toggle pressed on
			if (GM.mousePressedLeft): 
				self.pressed = True
			
			#set state based off of pressed
			self.state = "press" if self.pressed else "hover"
		
		#if mouse button was just released on us, trigger a press 
		if (GM.mouseReleasedLeft and self.pressed):
			GM.selection = self
			self.pressed = False
			
		#rotate when R is pressed if selected
		if (GM.selection == self and GM.rDown):
			self.setRotation(self.noSnapRot + (GM.mouseDy- GM.mouseDx)/2)
			
		#scale when E is pressed if selected
		if (GM.selection == self and GM.eDown):
			self.setScale(self.noSnapScale + (GM.mouseDy- GM.mouseDx)/100)
			
		#if pressed, move with mouse
		if (self.pressed):
			#get distance mouse moved since last frame, and update position accordingly
			self.x += GM.mouseDx
			self.y += GM.mouseDy
			self.rect.centerx = self.x
			self.rect.centery = self.y