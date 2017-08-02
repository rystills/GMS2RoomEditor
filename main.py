#Import Modules
import sys
#add class dir to path so we can import classes freely
sys.path.insert(1,"classes")
import GM
import pygame
import util

#main function: init game, then run the core game loop
def main():
	#initialize the pygame engine
	pygame.init()
	#call GameManager setup
	GM.init(1,1)
	
	util.initMainMenu()
	
	#Main Loop; runs until game is exited
	while GM.running:
		#update the game, exiting immediately if the user quit
		if (GM.tick()):
			break		
		GM.render()
	
#this calls the 'main' function when this script is executed directly
if __name__ == "__main__":
	main()