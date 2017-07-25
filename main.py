#Import Modules
import pygame, os
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, RLEACCEL
from tkinter import Tk
from tkinter.filedialog import askopenfilename

#static main game class; houses most game related variables and methods
class GM(object):
	#init game vars
	@staticmethod
	def setup(screenWidthIn, screenHeightIn):
		#init screen width and height (in pixels)
		GM.screenWidth = screenWidthIn
		GM.screenHeight = screenHeightIn
		
		#init fonts (each text size should have its own font)
		GM.fontSmall = pygame.font.Font(None, 24)
		
		#init game-related variables
		GM.running = True
		GM.deltaTime = 0
		GM.clock = pygame.time.Clock()
		
		#init input vars
		GM.mousePressedLeft = False
		GM.mouseDownLeft = False
		GM.mouseReleasedLeft = False
		
		#store object collections
		GM.activeButtons = object
	
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
	
	#update game
	@staticmethod
	def tick():
		#update simulation deltaTime
		GM.deltaTime = GM.clock.tick(60) / 1000
		GM.updateMouseVars()
		GM.checkQuit()
	
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
		self.updateImage();
		self.pressed = False
		
	#update our drawSurface (only needs to happen when our color or text is altered)
	def updateImage(self):
		self.image = self.font.render(self.text, True, self.color)
		self.rect = self.image.get_rect();
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
		white = 200;
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
	with open("lastProject.cfg", "r+") as file:
		file.truncate()
		file.write(projName)
			
#open a file dialog box for the user to select the root directory of their desired GameMaker Studio 2 project	
def openProjectDirectory():
	root = Tk()
	root.withdraw()
	fileName = askopenfilename(title = "Select GameMaker Studio 2 Project File") 
	if (len(fileName) > 0):
		writeLastUsedProject(fileName)
	root.destroy()	

#this function is called when the program starts. it initializes everything it needs, then runs in a loop until the function returns
def main():
	#initialize the pygame engine
	pygame.init()
	#call GameManager setup
	GM.setup(240,120)
	#init screen and window caption
	screen = pygame.display.set_mode([GM.screenWidth, GM.screenHeight])
	pygame.display.set_caption("Room Editor")
	
	#create load project button
	btn = Button("Load Project",GM.fontSmall, GM.screenWidth/2, GM.screenHeight/2,openProjectDirectory)
	
	#Main Loop; runs until game is exited
	while GM.running:
		#update the game at a steady 60 fps if possible (divide by 1000 to convert from milliseconds to seconds)
		GM.tick();
		#update objects
		btn.update()
		#render the solid color (black) background to prepare the screen for a fresh game render
		screen.fill((0,0,0))
		#render objects
		screen.blit(btn.image, btn.rect)
		#push final screen render to the display	 
		pygame.display.flip()
	
#this calls the 'main' function when this script is executed directly
if __name__ == "__main__":
	main()