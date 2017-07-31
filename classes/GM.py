import pygame
from pygame.locals import KEYDOWN, K_r, K_e, K_RCTRL, K_LCTRL, K_RALT, K_LALT, K_DELETE, QUIT, K_ESCAPE
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
	
	#init mouse input vars
	this.mousePressedLeft = False
	this.mouseDownLeft = False
	this.mouseReleasedLeft = False
	
	#init mouse pos vars
	this.mouseX = this.mouseY = -1
	this.mouseDx = this.mouseDy = -1
	
	#init keyboard input vars
	this.rPressed = False
	this.rDown = False
	this.rReleased = False
	
	this.ePressed = False
	this.eDown = False
	this.eReleased = False
	
	this.ctrlPressed = False
	this.ctrlDown = False
	this.ctrlReleased = False
	
	this.altPressed = False
	this.altDown = False
	this.altReleased = False
	
	this.deletePressed = False
	this.deleteDown = False
	this.deleteReleased = False
	
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
	this.selection = []
	this.dragging = False
	this.selectedThisPress = False
	this.placingObject = False
	
	#store editor state related vars
	this.angleSnaps = True
	this.scaleSnaps = True
	this.moveSnaps = True
	
#update mouse state variables
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
		this.dragging = False
				
	#update mouse position and delta values
	newMousePos = pygame.mouse.get_pos()
	this.mouseDx = newMousePos[0] - this.mouseX
	this.mouseDy = newMousePos[1] - this.mouseY
	this.mouseX,this.mouseY = newMousePos
				
#update keyboard state vars
def updateKeyboardVars():
	#r button down
	if pygame.key.get_pressed()[K_r]:
		this.rPressed = not this.rDown
		this.rDown = True
		this.rReleased = False
	#r button up
	else:
		this.rReleased = this.rDown
		this.rDown = False
		this.rPressed = False
		
	#e button down
	if pygame.key.get_pressed()[K_e]:
		this.ePressed = not this.rDown
		this.eDown = True
		this.eReleased = False
	#r button up
	else:
		this.eReleased = this.rDown
		this.eDown = False
		this.ePressed = False
		
	#ctrl button down
	if (pygame.key.get_pressed()[K_RCTRL] or pygame.key.get_pressed()[K_LCTRL]):
		this.ctrlPressed = not this.ctrlDown
		this.ctrlDown = True
		this.ctrlReleased = False
	#ctrl button up
	else:
		this.ctrlReleased = this.ctrlDown
		this.ctrlDown = False
		this.ctrlPressed = False
		
	#alt button down
	if (pygame.key.get_pressed()[K_RALT] or pygame.key.get_pressed()[K_LALT]):
		this.altPressed = not this.altDown
		this.altDown = True
		this.altReleased = False
	#alt  button up
	else:
		this.altReleased = this.altDown
		this.altDown = False
		this.altPressed = False
		
	#delete button down
	if (pygame.key.get_pressed()[K_DELETE] or pygame.key.get_pressed()[K_DELETE]):
		this.deletePressed = not this.deleteDown
		this.deleteDown = True
		this.deleteReleased = False
	#delete button up
	else:
		this.deleteReleased = this.deleteDown
		this.deleteDown = False
		this.deletePressed = False
				
#check if the user has pressed the escape key or the close button, and if so, quit
def checkQuit():
	for event in pygame.event.get():
		if (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
			this.running = False
			return True
	
#draw a selection box around the currently selected object
def drawSelectionBox():
	if (len(this.selection) != 0):
		print(this.selection)
		for sel in this.selection:
			#draw a rect surrounding the selected object
			buffer = 5
			selRect = sel.rect
			pygame.draw.rect(this.screen,pygame.color.Color(255,0,0),
							pygame.rect.Rect(selRect.left - buffer, selRect.top - buffer, 
											selRect.width + 2*buffer, selRect.height + 2*buffer),2)
		
			#draw the current object rotation in small text
			this.screen.blit(this.fontSmall.render(str(sel.rot),True,pygame.color.Color(0,255,0)),
							(selRect.left - buffer, selRect.top - buffer - 10))
			
			#draw the current object scale in small text
			this.screen.blit(this.fontSmall.render(str(sel.scale),True,pygame.color.Color(0,255,255)),
							(selRect.left - buffer + 40, selRect.top - buffer - 10))
			
			#draw the current object position in small text
			this.screen.blit(this.fontSmall.render(str(sel.x) + ", " + str(sel.y),True,pygame.color.Color(255,0,255)),
							(selRect.left - buffer, selRect.top - buffer - 25))
			
	
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

#update current selection, deselecting if nothing was clicked
def updateSelection():
	#set selection to none if mouse was just released and we didn't just select something
	if (this.mouseReleasedLeft):
		if (this.selectedThisPress):
			this.selectedThisPress = False
		else:
			this.selection = []
	
	#kill all selected objects when delete is pressed
	if (this.deletePressed):
		for obj in this.selection:
			obj.kill()
		this.selection = []

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
	this.updateKeyboardVars()
	this.updateObjects()
	this.updateSelection()

#delete all UI objects
def clearUI():
	for i in this.objects:
		i.kill()
		
#update the display and width,height vars to the specified dimensions
def updateScreenDimensions(width,height):
	pygame.display.set_mode((width,height))
	this.screenWidth = width
	this.screenHeight = height