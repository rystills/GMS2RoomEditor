import pygame
from pygame.locals import RLEACCEL
import os
import GM
from button import Button
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from roomObject import RoomObject
import json

#get the value of val in the file located at filepath inFile
def getFileVal(inFile, val):
	with open(inFile) as f:
		return json.load(f)[val]

#search all sprite images in the project to locate the sprite image corresponding to the input image id
def findSpriteImageById(imgId):
	sprList = (next(os.walk(GM.sprDir))[1])
	for i in range(len(sprList)):
		spr = sprList[i]
		#store the first file in the directory with extension '.png'
		fName = next(file for file in os.listdir(os.path.join(GM.sprDir,spr)) if file.endswith(".png"))
		if (fName[:-4] == imgId):
			return fName
	return None
		
#prepare the main menu window size and buttons
def initMainMenu():
	GM.updateScreenDimensions(240,120)
	#create load project button
	GM.objects.add(Button("Load Project",GM.fontMedium, GM.screenWidth/2, GM.screenHeight/2 - 20, openProjectDirectory))
	#create open last project button
	GM.objects.add(Button("Open Last Project",GM.fontMedium, GM.screenWidth/2, GM.screenHeight/2 + 20, openLastProject))	
	
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
		objSpr,hasAlpha = loadObjectSprite(objList[i])
		GM.objectsLayer.add(Button(objList[i],GM.fontSmall,2,90*i,selectObject,[objList[i]],"left",objSpr,hasAlpha))
		
	#show rooms layer
	GM.roomsLayer.visible = True
	
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
	
#open the specified room, hide the rooms panel, and open the layers panel
def openRoom(rm):
	print("opening room: " + os.path.join(os.path.join(GM.rmDir,rm),rm + ".yy"))
	GM.activeRoom = rm
	GM.roomsLayer.visible = False
	GM.objectsLayer.visible = True
	GM.layersLayer.visible = True
	populateLayers()

#clear and re-populate the list of layers depending on the active room
def populateLayers():
	#clear all pre-existing layers
	GM.layersLayer.empty()
	
	#locate the file corresponding to the currently active room
	rmFile = os.path.join(os.path.join(GM.rmDir,GM.activeRoom),GM.activeRoom + ".yy")
	
	#grab the list of layers from the JSON dict
	print("loading layers from room: " + rmFile)
	JSONLayers = getFileVal(rmFile,"layers")
	
	#append the layer ids to a new list
	layerNames = [layer["name"] for layer in JSONLayers]
	
	#add each layer name to the layer list
	for i in range(len(layerNames)):
		GM.layersLayer.add(Button(layerNames[i],GM.fontSmall,2,45*i,selectLayer,[layerNames[i]],"left"))
		
	#set the active layer to the first layer by default
	GM.activeGMSLayer = layerNames[0]
	
#select the input layer
def selectLayer(layer):
	#do nothing if the desired layer is already selected
	if (not GM.activeGMSLayer == layer):
		GM.activeGMSLayer = layer
		#deselect all objects when switching layers
		GM.selection = []

#select the specified object
def selectObject(obj):
	print("selected object: " + obj)
	newObj = RoomObject(GM.mouseX,GM.mouseY,obj, 0,1)
	newObj.followMouse = True
	GM.roomObjects.add(newObj)
	GM.placingObject = True
		
#search all sprites in the project to locate the sprite name corresponding to the input sprite id
def findSpriteById(sprId):
	sprList = (next(os.walk(GM.sprDir))[1])
	for i in range(len(sprList)):
		spr = sprList[i]
		sprFile = os.path.join(os.path.join(GM.sprDir,spr),spr + ".yy")
		print("opening sprite: " + sprFile)
		#check if this sprite's id matches the desired sprite id
		imgId = getFileVal(sprFile,"id")
		if (imgId == sprId):
			print ("located sprite -- name: " + spr)
			return spr
	return None
		
#return the sprite image file corresponding to the input sprite name
def getSpriteImage(sprName):
	return next(file for file in os.listdir(os.path.join(GM.sprDir,sprName)) if file.endswith(".png"))

#determine whether or not a png file has an alpha channel by checking the correct byte
def pngHasAlpha(imgPath):
	with open(imgPath, "rb") as file:
		file.read(25)
		return file.read(1) == b'\x06'
	return False
	
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

#round input float to the nearest specified base
def roundBase(x, base=5, nRoundDigits = 0):
	#we are rounding to a whole number
	if (not nRoundDigits):
		return int(base * round(float(x)/base))
	#we are rounding to a decimal value, so lets convert that to a whole value then divide back 
	x*=10**nRoundDigits
	xR = int(base * round(float(x)/base))
	return float(xR)/10**nRoundDigits

#load the sprite corresponding to the passed in obj name
def loadObjectSprite(obj):
	#read the object file to get its sprite id
	objFile = os.path.join(os.path.join(GM.objDir,obj),obj + ".yy")
	print("opening object: " + objFile)
	sprId = getFileVal(objFile,"spriteId")
	print("sprite id: " + sprId)
	#in the case of an object with no sprite, return the default sprite
	if (sprId == "00000000-0000-0000-0000-000000000000"):
		return GM.noSpriteImg,True
	#search the sprites directory for the sprite whose id matches the object's sprite id
	sprName = findSpriteById(sprId)
	#check the directory of the found sprite for its image
	sprImgPath = os.path.join(os.path.join(GM.sprDir,sprName),getSpriteImage(sprName))
	#load the found image
	hasAlpha =  pngHasAlpha(sprImgPath)
	return loadImage(sprImgPath,hasAlpha),hasAlpha