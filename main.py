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
		GM.roomsLayer.add(Button(rmList[i],GM.fontSmall,2,45*i,openRoom,[rmList[i]],"left"))
		
	#create a button for each object
	objList = (next(os.walk(GM.objDir))[1])
	for i in range(len(objList)):
		GM.objectsLayer.add(Button(objList[i],GM.fontSmall,2,45*i,selectObject,[objList[i]],"left",loadObjectSprite(objList[i])))
		
	#show rooms and objects layers
	GM.roomsLayer.visible = True
	GM.objectsLayer.visible = True
	
#open the specified room
def openRoom(rm):
	print("opening room: " + os.path.join(os.path.join(GM.rmDir,rm),rm + ".yy"))
	#with open()

#get all contents of the specified file, stripped of newlines, and return it as a strong
def getFileContents(fName):
	fileString = ""
	with open(fName, "rt") as f:
		for line in f:
			fileString += line.strip()
	return fileString

#get a specific value from a parsed file string
def getFileVal(fStr, val):
	#first get start index
	startInd = fStr.find(val)
	#next get index of first : after that
	colInd = fStr.find(":",startInd)
	#finally, get the index of the next comma
	commaInd = fStr.find(",",colInd)
	#if there was no next comma, this index should be set to the end of the string
	if (commaInd == -1):
		commaInd = len(fStr)-1
		
	#now get the string from 1 past the colon, up to but not including the next comma or end of file
	newStr = fStr[colInd+1:commaInd]
	
	#finally, strip off whitespace, commas, and double quotation marks
	return newStr.strip().strip(",").strip('"')

#search all sprite images in the project to locate the sprite image corresponding to the input image id
def findSpriteImageById(imgId):
	sprList = (next(os.walk(GM.sprDir))[1])
	for i in range(len(sprList)):
		spr = sprList[i]
		#store the first file in the directory with extension '.png'
		fName = next(file for file in os.listdir(os.path.join(GM.sprDir,spr)) if file.endswith(".png"))
		if (fName[:-4] == imgId):
			return fName
		
#search all sprites in the project to locate the sprite name corresponding to the input sprite id
def findSpriteById(sprId):
	sprList = (next(os.walk(GM.sprDir))[1])
	for i in range(len(sprList)):
		spr = sprList[i]
		sprFile = os.path.join(os.path.join(GM.sprDir,spr),spr + ".yy")
		print("opening sprite: " + sprFile)
		#check if this sprite's id matches the desired sprite id
		fStr = getFileContents(sprFile)
		imgId = getFileVal(fStr,"id")
		if (imgId == sprId):
			print ("located sprite -- name: " + spr)
			return spr
		
#return the sprite image file corresponding to the input sprite name
def getSpriteImage(sprName):
	return next(file for file in os.listdir(os.path.join(GM.sprDir,sprName)) if file.endswith(".png"))

#select the specified object
def selectObject(obj):
	print("selected object: " + obj)

#load the sprite corresponding to the passed in obj name
def loadObjectSprite(obj):
	#read the object file to get its sprite id
	objFile = os.path.join(os.path.join(GM.objDir,obj),obj + ".yy")
	print("opening object: " + objFile)
	fStr = getFileContents(objFile)
	sprId = getFileVal(fStr,"spriteId")
	print("sprite id: " + sprId)
	#search the sprites directory for the sprite whose id matches the object's sprite id
	sprName = findSpriteById(sprId)
	#check the directory of the found sprite for its image
	sprImgPath = os.path.join(os.path.join(GM.sprDir,sprName),getSpriteImage(sprName))
	#load the found image
	return GM.loadImage(sprImgPath)

#main function: init game, then run the core game loop
def main():
	#initialize the pygame engine
	pygame.init()
	#call GameManager setup
	GM.init(240,120)
	GM.roomsLayer.visible = False
	GM.objectsLayer.visible = False
	
	#create load project button
	GM.objects.add(Button("Load Project",GM.fontMedium, GM.screenWidth/2, GM.screenHeight/2 - 20, openProjectDirectory))
	#create open last project button
	GM.objects.add(Button("Open Last Project",GM.fontMedium, GM.screenWidth/2, GM.screenHeight/2 + 20, openLastProject))
	
	#Main Loop; runs until game is exited
	while GM.running:
		#update the game, exiting immediately if the user quit
		if (GM.tick()):
			break		
		GM.render()
	
#this calls the 'main' function when this script is executed directly
if __name__ == "__main__":
	main()