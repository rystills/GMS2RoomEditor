#Import Modules
import pygame, os
from pygame.locals import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RETURN, K_ESCAPE, K_f, K_q, RLEACCEL
from tkinter import *
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
		GM.fontSmall = pygame.font.Font(None, 12)
		
		#init game-related variables
		GM.running = True
		GM.deltaTime = 0
		GM.clock = pygame.time.Clock()
		
		#init input vars
		GM.mousePressedLeft = False
		GM.mouseDownLeft = False
		GM.mouseReleasedLeft = False
	
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
class Button():
	#button init; store this button's text string and font
	def __init__(self,text,font,x,y,align="center"):
		self.text = text
		self.font = font
		self.x = x
		self.y = y
		self.align = align
		self.calculateBounds()
		self.pressed = False
		
	#calculate the top, bottom, left, and right bounds of this button
	def calculateBounds(self):
		size = self.font.size(self.text)
		self.width = size[0]
		self.height = size[1]
		
	#return whether or not the point located at px,py is contained in our bounds
	def pointInBounds(self,pos):
		#first calculate our bounds based off of our extends and alignment
		left = self.x - (0 if self.align == "left" else self.width/2)
		right = self.x + (self.width if self.align == "left" else self.width/2)
		top = self.y
		bottom = self.y - self.height
		
		#now determine whether or not the point is in our calculated bounds
		return pos[0] >= left and pos[0] <= right and pos[1] <= top and pos[1] >= bottom
	
	#update button state based on mouse interaction
	def update(self):
		#check mouse button status
		#check if mouse is on this button 
		self.state = "neutral"
		if (self.pointInBounds(pygame.mouse.get_pos())):
			#if mouse button was just pressed on us, toggle pressed on
			if (GM.mousePressedLeft): 
				self.pressed = True
			
			#if mouse button was just released on us, trigger a press 
			if (GM.mouseReleasedLeft and self.pressed):
				#script_execute(self.function);
				print("button pressed")
			
			#set state based off of pressed
			self.state = "press" if self.pressed else "hover"
		
		
		#if mouse button is not held down, toggle pressed off
		if (not GM.mouseDownLeft): 
			self.pressed = False
		
		'''#color blend based off of state
		self.blendWhiteness = 200;
		if (self.state == "press") {
			self.blendWhiteness = 145;
		}
		else if (self.state == "hover") {
			self.blendWhiteness = 255;
		}
		image_blend = make_color_rgb(self.blendWhiteness,self.blendWhiteness,self.blendWhiteness);'''

#this function is called when the program starts. it initializes everything it needs, then runs in a loop until the function returns
def main():
	#initialize the pygame engine
	pygame.init()
	#call GameManager setup
	GM.setup(240,120)
	#init screen and window caption
	screen = pygame.display.set_mode([GM.screenWidth, GM.screenHeight])
	pygame.display.set_caption("Room Editor")
	#Main Loop; runs until game is exited
	while GM.running:
		#update the game at a steady 60 fps if possible (divide by 1000 to convert from milliseconds to seconds)
		GM.tick();
		#render the solid color (cool green) background to prepare the screen for a fresh game render
		screen.fill((160,200,160))
		#push final screen render to the display	 
		pygame.display.flip()
	
#this calls the 'main' function when this script is executed directly
if __name__ == "__main__":
	main()