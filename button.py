'''
Created on Jul 26, 2017

@author: Ryan
'''
import pygame
import GM
#simple mouse-based button class
class Button(pygame.sprite.Sprite):
	#button init; store this button's properties and prepare its surface
	def __init__(self,text,font,x,y,function,args=[],align="center"):
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
		self.updateImage()
		self.pressed = False
		self.layer = None
		
	#update our drawSurface (only needs to happen when our color or text is altered)
	def updateImage(self):
		self.image = self.font.render(self.text, True, self.color)
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