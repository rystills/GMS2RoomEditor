import zipfile
import os
import fnmatch
import compileall
#import shutil

projectName = "GMS2 Room Editor"
#change default build folder name to project name
os.rename(os.path.join(os.path.join(os.getcwd(),"build"),"exe.win32-3.2"), os.path.join(os.path.join(os.getcwd(),"build"),projectName))

#replace all .py files with compiled pyc files to speed up execution and reduce file size
for root, dirnames, filenames in os.walk(os.path.join("build",projectName)):
	for filename in fnmatch.filter(filenames, '*.py'): #replace all .py files with pre-compiled .pyc files
		curFile = os.path.join(root, filename)
		compileall.compile_file(curFile)
		os.remove(curFile)
		#python 3.2 will automatically change the extension from .py to .cpython-32.pyc, and move the file into a directory called __pycache__
		#move that file back out of the __pycache__ directory and replace the extension to simply .pyc
		os.rename(os.path.join(os.path.join(root,"__pycache__"),filename[:-3]+".cpython-32.pyc"),os.path.join(root,filename[:-3]+".pyc"))
		#if the __pycache__ folder is now empty (meaning either it was created when we compiled this file, or
		#it was created at some other time but never populated) delete it
		if not os.listdir(os.path.join(root,"__pycache__")):
			os.rmdir(os.path.join(root,"__pycache__"))