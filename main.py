#Import Modules
import pygame, os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import GM
from layer import Layer
from button import Button
			
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