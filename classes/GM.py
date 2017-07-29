import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE
from layer import Layer
import sys
from util import *
#set 'this' to point to this module, so we can maintain module-wide globals
this = sys.modules[__name__]

#GameManager module; houses most game related variables and methods
def init(screenWidthIn, screenHeightIn):
	#store base project directories
	this.rootDir = os.path.split(os.path.abspath(sys.argv[0]))[0]
	this.rootImgDir = os.path.join(this.rootDir,"images")
	
	#init screen width and height (in pixels)
	this.screenWidth = screenWidthIn
	this.screenHeight = screenHeightIn
	
	#set window position before pygame init
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (160,90)
	
	#init fonts (each text size should have its own font)
	this.fontDir = os.path.join(this.rootDir,"fonts")
	this.fontSmall = pygame.font.Font(os.path.join(this.fontDir,"freesansbold.ttf"), 12)
	this.fontMedium = pygame.font.Font(os.path.join(this.fontDir,"freesansbold.ttf"), 24)
	this.fontLarge = pygame.font.Font(os.path.join(this.fontDir,"freesansbold.ttf"), 48)
	
	#init game-related variables
	this.running = True
	this.deltaTime = 0
	this.clock = pygame.time.Clock()
	
	#init input vars
	this.mousePressedLeft = False
	this.mouseDownLeft = False
	this.mouseReleasedLeft = False
	
	#store object collections
	this.objects = pygame.sprite.LayeredUpdates() 
	this.roomsLayer = Layer(0,0,100,900,"Select Room")
	this.objectsLayer = Layer(1500,0,100,900,"Select Object")
	
	#init screen and window caption
	this.screen = pygame.display.set_mode([this.screenWidth, this.screenHeight])
	pygame.display.set_caption("Room Editor")
	
	#store room objects
	this.roomObjects = pygame.sprite.LayeredUpdates()
	
	#load image for objects with no sprite
	this.noSpriteImg = loadImage(os.path.join(this.rootImgDir,"noSprite.png"), True)
	
	#store vars relating to room object manipulation
	this.selection = None
	this.selectedThisPress = False
	this.placingObject = False
	
#update mouse click and press variables
def updateMouseVars():
	#left mouse button down
	if (pygame.mouse.get_pressed()[0]):
		this.mousePressedLeft = not this.mouseDownLeft
		this.mouseDownLeft = True
		this.mouseReleasedLeft = False
	#left mouse button up
	else:
		this.mouseReleasedLeft = this.mouseDownLeft
		this.mouseDownLeft = False
		this.mousePressedLeft = False
		
		if (this.mouseReleasedLeft):
			if (this.selectedThisPress):
				this.selectedThisPress = False
			else:
				#set selection to none if mouse was just released
				this.selection = None
		
#check if the user has pressed the escape key or the close button, and if so, quit
def checkQuit():
	for event in pygame.event.get():
		if (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
			this.running = False
			return True
	
#draw a selection box around the currently selected object
def drawSelectionBox():
	if (this.selection):
		buffer = 5
		selRect = this.selection.rect
		pygame.draw.rect(this.screen,pygame.color.Color(255,0,0),
						pygame.rect.Rect(selRect.left - buffer, selRect.top - buffer, selRect.width + 2*buffer, selRect.height + 2*buffer),2)
	
#render all objects to the screen	
def render():
	#render the solid color (black) background to prepare the screen for a fresh game render
	this.screen.fill((0,0,0))
	#render layers
	this.roomsLayer.render()
	this.screen.blit(this.roomsLayer.image,this.roomsLayer.rect)
	this.objectsLayer.render()
	this.screen.blit(this.objectsLayer.image,this.objectsLayer.rect)
	#render objects
	this.objects.draw(this.screen)
	#render room objects
	this.roomObjects.draw(this.screen)
	#draw selection box around selected object
	this.drawSelectionBox()
	
	#push final screen render to the display	 
	pygame.display.flip()

#update all objects
def updateObjects():
	#update objects
	for i in this.objects:
		i.update()
	#update room objects
	for i in this.roomObjects:
		i.update()
	#update rooms and objects lists
	this.roomsLayer.update()
	this.objectsLayer.update()

#update game
def tick():
	#update simulation deltaTime, running at 60 fps / 1000 milliseconds if possible
	this.deltaTime = this.clock.tick(60) / 1000
	#if the user quit, don't bother doing anything else
	if (this.checkQuit()):
		return True
	this.updateMouseVars()
	this.updateObjects()

#delete all UI objects
def clearUI():
	for i in this.objects:
		i.kill()
		
#update the display and width,height vars to the specified dimensions
def updateScreenDimensions(width,height):
	pygame.display.set_mode((width,height))
	this.screenWidth = width
	this.screenHeight = height