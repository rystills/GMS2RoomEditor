#Import Modules
import pygame, os, sys
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, RLEACCEL
from tkinter import Tk
from tkinter.filedialog import askopenfilename

#static main game class; houses most game related variables and methods
class GM(object):
	#init game vars
	@staticmethod
	def init(screenWidthIn, screenHeightIn):
		#store directories
		GM.rootDir = os.path.split(os.path.abspath(sys.argv[0]))[0]
		
		#init screen width and height (in pixels)
		GM.screenWidth = screenWidthIn
		GM.screenHeight = screenHeightIn
		
		#init fonts (each text size should have its own font)
		GM.fontDir = os.path.join(GM.rootDir,"fonts")
		GM.fontSmall = pygame.font.Font(os.path.join(GM.fontDir,"freesansbold.ttf"), 18)
		
		#init game-related variables
		GM.running = True
		GM.deltaTime = 0
		GM.clock = pygame.time.Clock()
		
		#init input vars
		GM.mousePressedLeft = False
		GM.mouseDownLeft = False
		GM.mouseReleasedLeft = False
		
		#store object collections
		GM.objects = pygame.sprite.LayeredUpdates() 
		GM.roomsLayer = Layer(0,0,150,900)
		GM.objectsLayer = Layer(1450,0,150,900)
		
		#init screen and window caption
		GM.screen = pygame.display.set_mode([GM.screenWidth, GM.screenHeight])
		pygame.display.set_caption("Room Editor")
	
	#update mouse click and press variables
	@staticmethod
	def updateMouseVars():
		#left mouse button down
		if (pygame.mouse.get_pressed()[0]):
			GM.mousePressedLeft = not GM.mouseDownLeft
			GM.mouseDownLeft = True
			GM.mouseReleasedLeft = False
		#left mouse button up
		else:
			GM.mouseReleasedLeft = GM.mouseDownLeft
			GM.mouseDownLeft = False
			GM.mousePressedLeft = False
			
	#check if the user has pressed the escape key or the close button, and if so, quit
	@staticmethod
	def checkQuit():
		for event in pygame.event.get():
			if (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
				GM.running = False
				return True
		
	#render all objects to the screen	
	@staticmethod
	def render():
		#render the solid color (black) background to prepare the screen for a fresh game render
		GM.screen.fill((0,0,0))
		#render layers
		GM.roomsLayer.render()
		GM.screen.blit(GM.roomsLayer.image,GM.roomsLayer.rect)
		GM.objectsLayer.render()
		GM.screen.blit(GM.objectsLayer.image,GM.objectsLayer.rect)
		#render objects
		GM.objects.draw(GM.screen)
		#push final screen render to the display	 
		pygame.display.flip()
	
	#update all objects
	@staticmethod
	def updateObjects():
		for i in GM.objects:
			i.update()
		GM.roomsLayer.update()
		GM.objectsLayer.update()
	
	#update game
	@staticmethod
	def tick():
		#update simulation deltaTime, running at 60 fps / 1000 milliseconds if possible
		GM.deltaTime = GM.clock.tick(60) / 1000
		#if the user quit, don't bother doing anything else
		if (GM.checkQuit()):
			return True
		GM.updateMouseVars()
		GM.updateObjects()
	
	#load an image, optionally setting a colorkey - adapted from the pygame chimp example
	@staticmethod
	def loadImage(imageName, convertAlpha=False, colorkey=None): 
		fullname = os.path.join(imageName)
		try:
			image = pygame.image.load(fullname)
		except:
			print('Cannot load image:', fullname)
			raise SystemExit
	
		#convert_alpha should be used only for images with per-pixel alpha transparency
		image = image.convert() if not convertAlpha else image.convert_alpha()
		if colorkey is not None:
			if colorkey is -1:
				colorkey = image.get_at((0,0))
			image.set_colorkey(colorkey, RLEACCEL)
		return image
	
	#delete all UI objects
	@staticmethod
	def clearUI():
		for i in GM.objects:
			i.kill()
			
	#update the display and width,height vars to the specified dimensions
	@staticmethod
	def updateScreenDimensions(width,height):
		pygame.display.set_mode((width,height))
		GM.screenWidth = width
		GM.screenHeight = height
		
#simple class that stores and renders a group of objects
class Layer(pygame.sprite.Sprite):
	def __init__(self,x,y,width,height):
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
			self.scrollBarRect = pygame.rect.Rect(self.image.get_width()-20,
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
			
#store a local reference to the last used project for future use
def writeLastUsedProject(projName):
	with open("lastProject.cfg", "w") as file:
		file.truncate()
		file.write(projName)
			
#open a file dialog box for the user to locate and select their desired GameMaker Studio 2 project
def openProjectDirectory():
	root = Tk()
	root.withdraw()
	projFile = askopenfilename(title = "Select GameMaker Studio 2 Project File")
	root.destroy()
	if (len(projFile) > 0):
		#normalize the path returned by tkinter to the current OS path type
		projFile = os.path.normpath(projFile)
		writeLastUsedProject(projFile)
		openProject(projFile)
	
#open the last project stored in lastProject.cfg, if one exists
def openLastProject():
	if (os.path.isfile("lastProject.cfg")):
		with open("lastProject.cfg", "r") as file:
			projFile = file.readline().strip()
			if (len(projFile) > 1):
				openProject(projFile)

#open the project pointed to by projFile
def openProject(projFile):
	#init projet directories
	GM.projDir = projFile[:projFile.rfind(os.path.sep)]
	print("opening project: " + GM.projDir)
	GM.sprDir = os.path.join(GM.projDir,"sprites")
	GM.objDir = os.path.join(GM.projDir,"objects")
	GM.rmDir = os.path.join(GM.projDir,"rooms")
	GM.clearUI()
	GM.updateScreenDimensions(1600,900)
	#create a button for each room
	rmList = (next(os.walk(GM.rmDir))[1])
	for i in range(len(rmList)):
		GM.roomsLayer.add(Button(rmList[i],GM.fontSmall,30,30 + 50*i,openRoom,[rmList[i]],"left"))
		
	#create a button for each object
	objList = (next(os.walk(GM.objDir))[1])
	for i in range(len(objList)):
		GM.objectsLayer.add(Button(objList[i],GM.fontSmall,30,30 + 50*i,selectObject,[objList[i]],"left"))
	
#open the specified room
def openRoom(rm):
	print("opening room: " + os.path.join(os.path.join(GM.rmDir,rm),rm + ".yy"))
	#with open()
	
#select the specified object
def selectObject(obj):
	print("opening object: " + os.path.join(os.path.join(GM.objDir,obj),obj + ".yy"))

#main function: init game, then run the core game loop
def main():
	#initialize the pygame engine
	pygame.init()
	#call GameManager setup
	GM.init(240,120)
	
	#create load project button
	GM.objects.add(Button("Load Project",GM.fontSmall, GM.screenWidth/2, GM.screenHeight/2 - 20, openProjectDirectory))
	#create open last project button
	GM.objects.add(Button("Open Last Project",GM.fontSmall, GM.screenWidth/2, GM.screenHeight/2 + 20, openLastProject))
	
	#Main Loop; runs until game is exited
	while GM.running:
		#update the game, exiting immediately if the user quit
		if (GM.tick()):
			break		
		GM.render()
	
#this calls the 'main' function when this script is executed directly
if __name__ == "__main__":
	main()