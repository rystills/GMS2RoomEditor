from cx_Freeze import setup, Executable
import pygame._view
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

excludes = ["numpy","wx","lib2to3","urllib","pydoc"]
	
includes = ["re","pygame", "pygame._view", "tkinter"]
includefiles = ['fonts']

setup(name = "GMS2 Room Editor",version = "1",description = "External Room Editor for GameMaker Studio 2",executables = [Executable("main.py", base = base)], options = {"build_exe": {"excludes":excludes, "includes":includes, 'include_files':includefiles}})