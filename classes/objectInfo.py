'''
Created on Aug 22, 2017

@author: Ryan
'''

#simple class that stores info about a GMS object
class ObjectInfo():
	def __init__(self,objName,objId,img,imgHasAlpha):
		self.objName = objName
		self.objId = objId
		self.img = img
		self.imgHasAlpha = imgHasAlpha