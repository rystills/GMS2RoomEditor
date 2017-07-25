#Import Modules
import pygame, os
from pygame.locals import QUIT, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RETURN, K_ESCAPE, K_f, K_q, RLEACCEL
from tkinter import *
from tkinter.filedialog import askopenfilename

#main game class; houses most game related variables and methods
class GameManager():
	def __init__(self, screenWidthIn, screenHeightIn):
		#init screen width and height (in pixels)
		self.screenWidth = screenWidthIn
		self.screenHeight = screenHeightIn
		
		#init fonts (each text size should have its own font)
		self.fontSmall = pygame.font.Font(None, 12)
		
		#init game-related variables
		self.running = True
		self.deltaTime = 0
		self.clock = pygame.time.Clock()
		
	#update game
	def tick(self):
		#update simulation deltaTime
		self.deltaTime = self.clock.tick(60) / 1000

#this function is called when the program starts. it initializes everything it needs, then runs in a loop until the function returns
def main():
	#initialize the pygame engine
	pygame.init()
	#instantiate class to maintain game state
	gameManager = GameManager(1920,1080)
	#init screen and window caption
	screen = pygame.display.set_mode([gameManager.screenWidth, gameManager.screenHeight])
	pygame.display.set_caption("Room Editor")
	#Main Loop; runs until game is exited
	while gameManager.running:
		#update the game at a steady 60 fps if possible (divide by 1000 to convert from milliseconds to seconds)
		gameManager.tick();
		#render the solid color (cool green) background to prepare the screen for a fresh game render
		screen.fill((160,200,160))
		#push final screen render to the display	 
		pygame.display.flip()
	
#this calls the 'main' function when this script is executed directly
if __name__ == "__main__":
	main()