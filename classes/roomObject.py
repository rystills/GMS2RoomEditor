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
		self.noSnapX = self.x
		self.y = y
		self.noSnapY = self.y
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
		
	#set rotation to newRot, snapping if angleSnaps are enabled
	def setRotation(self,newRot):
		self.noSnapRot = newRot % 360
		roundRot = roundBase(self.noSnapRot) % 360 if GM.angleSnaps else self.noSnapRot
		#do nothing if new rotation is the same as old rotation
		if (roundRot != self.rot):
			self.rot = roundRot
			#use rotozoom if we are rotated and scaled
			if (self.scale != 1):
				self.image = pygame.transform.rotozoom(self.baseImage,roundRot,self.scale)
			#we are just rotated
			else:
				self.image = pygame.transform.rotate(self.baseImage,roundRot)
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
		
	#set scale to newScale, snapping if scaleSnaps are enabled	
	def setScale(self,newScale):
		self.noSnapScale = max(newScale,0.05)
		roundScale = roundBase(self.noSnapScale,5,2) if GM.scaleSnaps else self.noSnapScale
		#do nothing if new scale is the same as old scale
		if (roundScale != self.scale):
			self.scale = roundScale			
			scaledWidth = int(self.baseImage.get_width()*self.scale)
			scaledHeight = int(self.baseImage.get_height()*self.scale)
			#use rotozoom if we are rotated and scaled
			if (self.rot != 0):
				self.image = pygame.transform.rotozoom(self.baseImage,self.rot,self.scale)
			#we are just scaled
			else:
				self.image = pygame.transform.scale(self.baseImage,(scaledWidth,scaledHeight))
			#convert with alpha
			if (self.imgHasAlpha):
				self.image = self.image.convert_alpha()
			#convert without alpha
			else:
				self.image = self.image.convert()
			#update rect to scaled image, preserving old rect center
			self.rect = self.image.get_rect()
			self.rect.centerx = self.x
			self.rect.centery = self.y
			
	#move to position x,y, snapping to grid if moveSnaps are enabled
	def move(self,x,y):
		self.noSnapX = x
		self.noSnapY = y
		roundX = roundBase(self.noSnapX,32) if GM.moveSnaps else self.noSnapX
		roundY = roundBase(self.noSnapY,32) if GM.moveSnaps else self.noSnapY
		self.rect.center = (roundX,roundY)
		self.x,self.y = self.rect.center
		
	def update(self):
		#if we are in follow mouse mode, don't do anything until we detect a leftclick
		if (self.followMouse):
			self.move(GM.mouseX,GM.mouseY)
			#exit follow mode when mouse is pressed	
			if (GM.mousePressedLeft):
				self.followMouse = False
				#set selection to this object, now that we've placed it
				GM.selection = [self]
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
				if (GM.altDown):
					self.pressed = False
					if (self in GM.selection):
						GM.selection.remove(self)
				else:
					self.pressed = True
					GM.dragging = True
					
					if (GM.ctrlDown):
						if (not self in GM.selection):
							GM.selection.append(self)
					elif (not self in GM.selection):
						GM.selection = [self]
					self.pressed = False
				#tell the game mamanger that a selection was just changed, so that it does not de-select us
				GM.selectedThisPress = True
			
			#if mouse is released, reset no snap position to snap position
			else:
				self.noSnapX,self.noSnapY = self.x,self.y	
			
			#set state based off of pressed
			self.state = "press" if self.pressed else "hover"
			
		#rotate when R is pressed if selected
		if (self in GM.selection and GM.rDown):
			self.setRotation(self.noSnapRot + (GM.mouseDy- GM.mouseDx)/2)
		#if R is released, set no snap rotation to snap rotation
		else:
			self.noSnapRot = self.rot
			
		#scale when E is pressed if selected
		if (self in GM.selection and GM.eDown):
			self.setScale(self.noSnapScale + (GM.mouseDy- GM.mouseDx)/400)
		#if E is released, set no snap scale to snap scale
		else:
			self.noSnapScale = self.scale
			
		#if pressed, move with mouse
		if (GM.dragging and self in GM.selection):
			#get distance mouse moved since last frame, and update position accordingly
			self.move(self.noSnapX + GM.mouseDx, self.noSnapY + GM.mouseDy)