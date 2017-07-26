'''
Created on Jul 26, 2017

@author: Ryan
'''
import pygame
import GM

#simple class that stores and renders a group of objects
class Layer(pygame.sprite.Sprite):
	def __init__(self,x,y,width,height,scrollbarPos = "right"):
		self.image = pygame.surface.Surface((width,height))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x,y)
		self.containedObjects = pygame.sprite.LayeredUpdates()
		#scroll x and y values, measured as a fraction of the scroll height difference
		self.scrollX = 0
		self.scrollY = 0
		self.scrollHeightDiff = 0
		self.scrollBarDragging = False
		self.scrollBarRect = None
		self.dragStartPos = (0,0)
		self.scrollbarColor = pygame.Color(200,200,200,255)
		self.scrollbarPos = scrollbarPos
	
	#add the input object to this layer
	def add(self,obj):
		self.containedObjects.add(obj)
		obj.layer = self
		self.resizeScrollbar()
		
	#adjust this layer's scrollbar so that its size and scroll bounds match the extents of the contained objects
	def resizeScrollbar(self):
		#first find the highest and lowest objects
		self.topY = self.bottomY = None
		for i in self.containedObjects:
			if (self.topY == None or i.rect.top < self.topY):
				self.topY = i.rect.top
			if (self.bottomY == None or i.rect.bottom > self.bottomY):
				self.bottomY = i.rect.bottom
		
		#now determine the difference between the top y and bottom y and this layer's height
		self.scrollHeightDiff = (self.bottomY - self.topY) - self.image.get_height()
		if (self.scrollHeightDiff > 0):
			#set scrollbar height to the proportion of the view to the range of content
			self.scrollbarHeight = self.image.get_height() * (self.image.get_height() / (self.bottomY - self.topY))
	
	#render all contained objects to our surface
	def render(self):
		#clear view area to black
		self.image.fill((0,0,0))
		#draw all objects
		scrollDistance = self.scrollY * self.scrollHeightDiff
		for i in self.containedObjects:
			#move rect based on scroll value
			oldCentery = i.rect.centery
			i.rect.centery -= self.topY
			i.rect.centery -= scrollDistance
			self.image.blit(i.image,i.rect)
			i.rect.centery = oldCentery
		
		#draw the scrollbar, if it exists
		if (self.scrollHeightDiff > 0):
			pygame.draw.rect(self.image,self.scrollbarColor,self.scrollBarRect)
			
	#update this layer's scrollbar and modify scroll values accordingly
	def updateScrollbar(self):
		#update scrollbar if it exists
		if (self.scrollHeightDiff > 0):
			self.scrollBarRect = pygame.rect.Rect(self.image.get_width()-20 if self.scrollbarPos == "right" else 0,
				(self.image.get_height() - self.scrollbarHeight) * self.scrollY,20,self.scrollbarHeight)
			
			#move scrollbar when dragged
			hovering = False
			if (self.scrollBarRect.collidepoint(pygame.mouse.get_pos())):
				hovering = True
				#if mouse button was just pressed on the scrollbar, toggle pressed on
				if (GM.mousePressedLeft): 
					self.scrollBarDragging = True
					self.dragStartPos = pygame.mouse.get_pos()
			
			#if mouse is held on the scrollbar, drag it vertically 
			if (GM.mouseDownLeft):
				if (self.scrollBarDragging):
					#scroll as a percentage of the total scroll distance
					self.scrollY -= (self.dragStartPos[1] - pygame.mouse.get_pos()[1]) / (self.image.get_height() - self.scrollbarHeight)
					#keep scroll value bounded
					if self.scrollY < 0:
						self.scrollY = 0
					if self.scrollY > 1:
						self.scrollY = 1
					#update relative drag pos to current mouse pos
					self.dragStartPos = pygame.mouse.get_pos()
			#release scrollbar when no longer dragging
			else:
				self.scrollBarDragging = False
				
			#color blend scrollbar based off of state
			white = 200
			if (self.scrollBarDragging):
				white = 145
			elif (hovering):
				white = 255	
			#update our draw surface if our color changed
			if (white != self.scrollbarColor.r):
				self.scrollbarColor = pygame.Color(white,white,white,255)
			
	#update all contained objects
	def update(self):
		for i in self.containedObjects:
			#move object rect to its scroll and layer pos adjusted position before updating
			oldCenter = i.rect.center
			i.rect.centery -= self.topY
			i.rect.centery -= (self.scrollY * self.scrollHeightDiff)
			i.rect.top += self.rect.top
			i.rect.left += self.rect.left
			i.update()
			#move object rect back to its absolute position after updating
			i.rect.center = oldCenter
		self.updateScrollbar()