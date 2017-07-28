'''
Created on Jul 26, 2017

@author: Ryan
'''
import pygame
import GM
#simple mouse-based button class
class Button(pygame.sprite.Sprite):
	#button init; store this button's properties and prepare its surface
	def __init__(self,text,font,x,y,function,args=[],align="center",sprite=None, sprSize = 64):
		#Call the parent class (Sprite) constructor
		pygame.sprite.Sprite.__init__(self)
		self.text = text
		self.font = font
		self.x = x
		self.y = y
		self.function = function
		self.args = args
		self.align = align
		self.color = pygame.Color(200,200,200,255)
		self.pressed = False
		self.layer = None
		#spr is the passed on sprite, if any
		self.spr = sprite
		#sprSize is the target dimension (width and height) that we will scale to
		self.sprSize = sprSize
		if (self.spr != None):
			#scale the larger dimension to sprSize, in order to preserve aspect ratio
			sprDims = self.spr.get_size()
			#width is the larger dimension
			if (sprDims[0] > sprDims[1]):
				self.scaledSpr = pygame.transform.smoothscale(self.spr,(self.sprSize,int((self.sprSize/sprDims[0]) * sprDims[1])))
			#height is the larger or equal dimension
			else:
				self.scaledSpr = pygame.transform.smoothscale(self.spr,(int((self.sprSize/sprDims[1]) * sprDims[0]), self.sprSize))
			self.image = self.scaledSpr
			self.rect = self.image.get_rect()
		self.updateImage()
		
	#update our drawSurface (only needs to happen when our color or text is altered)
	def updateImage(self):
		#if we don't have a sprite, just re-render font. otherwise, redraw image first
		if (self.spr == None):
			self.image = self.font.render(self.text, True, self.color)
		else:
			self.image = self.scaledSpr
			self.image.blit(self.font.render(self.text,True,self.color),(0,0))
		self.rect = self.image.get_rect()
		if (self.align == "center"):
			self.rect.center = (self.x,self.y)
		else:
			self.rect.topleft = (self.x,self.y)
	
	#update button state based on mouse interaction
	def update(self):
		#check mouse button status
		#check if mouse is on this button 
		self.state = "neutral"
		if (self.rect.collidepoint(pygame.mouse.get_pos())):
			#if mouse button was just pressed on us, toggle pressed on
			if (GM.mousePressedLeft): 
				self.pressed = True
			
			#if mouse button was just released on us, trigger a press 
			if (GM.mouseReleasedLeft and self.pressed):
				self.function(*self.args)
			
			#set state based off of pressed
			self.state = "press" if self.pressed else "hover"
		
		
		#if mouse button is not held down, toggle pressed off
		if (not GM.mouseDownLeft): 
			self.pressed = False
		
		#color blend based off of state
		white = 200
		if (self.state == "press"):
			white = 145
		elif (self.state == "hover"):
			white = 255
		#update our draw surface if our color changed
		if (white != self.color.r):
			self.color = pygame.Color(white,white,white,255)
			self.updateImage()