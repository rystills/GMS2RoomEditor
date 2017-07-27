import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, RLEACCEL
from layer import Layer
import sys, os
#set 'this' to point to this module, so we can maintain module-wide globals
this = sys.modules[__name__]

#GameManager module; houses most game related variables and methods
def init(screenWidthIn, screenHeightIn):
	#store directories
	this.rootDir = os.path.split(os.path.abspath(sys.argv[0]))[0]
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
	this.objectsLayer = Layer(1500,0,100,900,"Select Object", "left")
	
	#init screen and window caption
	this.screen = pygame.display.set_mode([this.screenWidth, this.screenHeight])
	pygame.display.set_caption("Room Editor")

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
		
#check if the user has pressed the escape key or the close button, and if so, quit
def checkQuit():
	for event in pygame.event.get():
		if (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
			this.running = False
			return True
	
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
	#push final screen render to the display	 
	pygame.display.flip()

#update all objects

def updateObjects():
	for i in this.objects:
		i.update()
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
	
#load an image, optionally setting a colorkey - adapted from the pygame chimp example
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
def clearUI():
	for i in this.objects:
		i.kill()
		
#update the display and width,height vars to the specified dimensions
def updateScreenDimensions(width,height):
	pygame.display.set_mode((width,height))
	this.screenWidth = width
	this.screenHeight = height