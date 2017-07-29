import pygame
from pygame.locals import RLEACCEL
import os
import GM

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

#load the sprite corresponding to the passed in obj name
def loadObjectSprite(obj):
	#read the object file to get its sprite id
	objFile = os.path.join(os.path.join(GM.objDir,obj),obj + ".yy")
	print("opening object: " + objFile)
	fStr = getFileContents(objFile)
	sprId = getFileVal(fStr,"spriteId")
	print("sprite id: " + sprId)
	#in the case of an object with no sprite, return the default sprite
	if (sprId == "00000000-0000-0000-0000-000000000000"):
		return GM.noSpriteImg
	#search the sprites directory for the sprite whose id matches the object's sprite id
	sprName = findSpriteById(sprId)
	#check the directory of the found sprite for its image
	sprImgPath = os.path.join(os.path.join(GM.sprDir,sprName),getSpriteImage(sprName))
	#load the found image
	return loadImage(sprImgPath, pngHasAlpha(sprImgPath))