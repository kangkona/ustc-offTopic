
from ctypes import *
from ctypes.util import find_library

import   sys,os 

class Cmetspell:
	spelldll = None

	def __init__(self):
		pass
	
	def load(self):
		dllFilename = r'D:\essayscoring\trunk\src\essayscore\iwt\spellchecker\cmetspell.dll'
		dicFilename = r'D:\essayscoring\trunk\src\essayscore\iwt\spellchecker\dict'
		self.spelldll = cdll.LoadLibrary(dllFilename)
		self.spelldll.CmetspellInitialize()
		self.spelldll.CmetspellGetDicWords(dicFilename)
		
	def unload(self):
		self.spelldll.CmetspellUninitialize()
	
	def check(self, word):
		x = self.spelldll.CmetspellCheckWord(word)
		return x
		
		
if __name__ == "__main__":
	spell = Cmetspell()
	spell.load()
	print 'loaded'
	x = spell.check('i')
	print x
	x = spell.check('sutdent')
	print x
	spell.unload()