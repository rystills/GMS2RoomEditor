import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_DELETE, K_LCTRL, K_RCTRL, K_a, K_d, K_q
from layer import Layer
import sys, os
import util

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
	this.boxing = False
	this.boxStartPos = None
	this.selectionRect = None
	
	#init mouse pos vars
	this.mouseX = this.mouseY = -1
	this.mouseDx = this.mouseDy = -1
	
	#init keyboard input vars
	this.keysPressed = list(pygame.key.get_pressed())
	this.keysDown = list(this.keysPressed)
	this.keysReleased = list(this.keysPressed)
	
	#store object collections
	this.objects = pygame.sprite.LayeredUpdates() 
	this.roomsLayer = Layer(0,0,100,900,"Select Room")
	this.roomsLayer.visible = False
	this.objectsLayer = Layer(1500,0,100,900,"Select Object")
	this.objectsLayer.visible = False
	this.layersLayer = Layer(0,0,100,900,"Select Layer")
	this.layersLayer.visible = False
	
	#init screen and window caption
	this.screen = pygame.display.set_mode([this.screenWidth, this.screenHeight])
	pygame.display.set_caption("Room Editor")
	
	#store room objects
	this.roomObjects = pygame.sprite.LayeredUpdates()
	
	#load image for objects with no sprite
	this.noSpriteImg = util.loadImage(os.path.join(this.rootImgDir,"noSprite.png"), True)
	
	#store vars relating to room object manipulation
	this.selection = []
	this.dragging = False
	this.selectedThisPress = False
	this.placingObject = False
	
	#store editor state related vars
	this.angleSnaps = True
	this.scaleSnaps = True
	this.moveSnaps = True
	this.gridX = this.gridY = 1
	
	#store current room related vars
	this.activeRoom = None
	this.activeGMSLayer = None
	
#update mouse state variables
def updateMouseVars():
	#update mouse position and delta values
	newMousePos = pygame.mouse.get_pos()
	this.mouseDx = newMousePos[0] - this.mouseX
	this.mouseDy = newMousePos[1] - this.mouseY
	this.mouseX,this.mouseY = newMousePos
	
	#if the left mouse button is down, toggle it on and set pressed if this is the first frame
	if (pygame.mouse.get_pressed()[0]):
		this.mousePressedLeft = not this.mouseDownLeft
		#only set box start pos on the frame when the mouse is first pressed down
		if (this.mousePressedLeft):
			this.boxing = True
			this.boxStartPos = newMousePos
		this.mouseDownLeft = True
		this.mouseReleasedLeft = False
	#if the left mouse button is up, toggle it off and set released if this is the first frame
	else:
		this.mouseReleasedLeft = this.mouseDownLeft
		this.mouseDownLeft = False
		this.mousePressedLeft = False
		this.dragging = False
		
	this.updateSelectionRect()
		
#update the current selection rect, if it exists
def updateSelectionRect():
	if (this.boxing):
		#start by calculating the box dimensions from the start pos and current mouse pos
		left = min(this.boxStartPos[0],this.mouseX)
		top = min(this.boxStartPos[1],this.mouseY)
		right = max(this.boxStartPos[0],this.mouseX)
		bot = max(this.boxStartPos[1],this.mouseY)
		#create a rect for our box
		this.selectionRect = pygame.rect.Rect(left,top,right-left,bot-top)
		
#return whether or not the input object is in the correct room
def objectRoomActive(obj):
	return True if (not hasattr(obj,"room") or not obj.room) else obj.room == this.activeRoom

#return whether or not the input object is on an active GMS or editor layer
def objectLayerActive(obj):
	#if the object has no layer, then it is always active
	if (not obj.layer):
		return objectRoomActive(obj)
	
	#if the object layer is a GMS layer, test it against the active layer string
	if (type(obj.layer) is str):
		return objectRoomActive(obj) if obj.layer == this.activeGMSLayer else False
	
	#if the object layer is an editor layer, check if it is visible
	return objectRoomActive(obj) if obj.layer.visible else False

#select all objects in the selectionBox
def selectInBox():
	#set our selection to all colliding objects
	for obj in this.roomObjects:
		if ((objectLayerActive(obj)) and obj.rect.colliderect(this.selectionRect)):
			this.selection.append(obj)
				
#update keyboard state vars
def updateKeyboardVars():
	kp = pygame.key.get_pressed()
	for i in range(len(kp)):
		#if the key is down, toggle it on and set pressed if this is the first frame
		if (kp[i]):
			this.keysPressed[i] = not this.keysDown[i]
			this.keysDown[i] = True
			this.keysReleased[i] = False
		#if the key is up, toggle it off and set released if this is the first frame
		else:
			this.keysReleased[i] = this.keysDown[i]
			this.keysDown[i] = False
			this.keysPressed[i] = False

#check if the user has pressed the escape key or the close button, and if so, quit
def checkQuit():
	for event in pygame.event.get():
		if (event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE)):
			this.running = False
			return True
	
#if the user is actively creating a group selection rect, draw it
def drawSelectionRect():
	if (this.boxing):
		#draw a semi-transparent background to the selection
		seleBG = pygame.Surface((this.selectionRect.width,this.selectionRect.height))
		seleBG.set_alpha(64)
		seleBG.fill((0,255,0,))
		this.screen.blit(seleBG,(this.selectionRect.x,this.selectionRect.y))
		#draw the selection edges as a fully opague border line
		pygame.draw.rect(this.screen,pygame.color.Color(0,255,0),this.selectionRect,1)
	
#draw a selection box around the currently selected object
def drawSelectionBox():
	if (len(this.selection) != 0):
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
	if (this.roomsLayer.visible):
		this.roomsLayer.render()
		this.screen.blit(this.roomsLayer.image,this.roomsLayer.rect)
	if (this.layersLayer.visible):
		this.layersLayer.render()
		this.screen.blit(this.layersLayer.image,this.layersLayer.rect)
	if (this.objectsLayer.visible):
		this.objectsLayer.render()
		this.screen.blit(this.objectsLayer.image,this.objectsLayer.rect)
	#render objects
	for obj in this.objects:
		if (obj.visible and objectLayerActive(obj)):
			this.screen.blit(obj.image,obj.rect)
	#render room objects
	for obj in this.roomObjects:
		if (obj.visible and objectLayerActive(obj)):
			this.screen.blit(obj.image,obj.rect)
	#draw selection box around selected object
	this.drawSelectionBox()
	#if the user is actively creating a group selection rect, draw it
	this.drawSelectionRect()
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
			if (this.boxing):
				this.selectInBox()
				this.boxing = False
		
	#kill all selected objects when delete is pressed
	if (this.keysPressed[K_DELETE]):
		for obj in this.selection:
			obj.kill()
		this.selection = []
		
	#duplicate all selected objects when d is pressed, and place them in follow mouse mode
	if (this.keysPressed[K_d] and not this.placingObject):
		this.placingObject = True
		for obj in this.selection:
			newObj = obj.clone()
			newObj.followMouse = True
			newObj.followXOffset = this.mouseX - newObj.x
			newObj.followYOffset = this.mouseY - newObj.y
			
	#select all objects when ctrl + a is pressed
	if ((this.keysDown[K_LCTRL] or this.keysDown[K_RCTRL]) and (this.keysDown[K_a])):
		this.selection = []
		for obj in this.roomObjects:
			this.selection.append(obj)
			
	#return one menu when q is pressed
	if (this.keysPressed[K_q]):
		this.returnMenu()	
	
#return from one menu
def returnMenu():
	if (this.layersLayer.visible):
		this.roomsLayer.visible = True
	else:
		this.roomsLayer.visible = False
		util.initMainMenu()
	this.layersLayer.visible = False
	this.objectsLayer.visible = False
	
	#reset the selection and active layer when changing menues
	this.selection = []
	this.activeGMSLayer = None

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
	this.layersLayer.update()
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
	#if we just made a selection modification, don't start a selection box
	if (this.selectedThisPress):
		this.boxing = False
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