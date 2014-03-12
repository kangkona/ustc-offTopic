import locale
import clinkgrammar as clg
import atexit

class lp(object):

	def __init__(self):
		locale.setlocale(locale.LC_ALL,"en_US.UTF8")

		lp.parse_options = ParseOptions()
		lp.dictionary = Dictionary("en")
	
	def __del__(self):
		print "Deleting",self.__class__
		del lp.parse_options
		del lp.dictionary
	
	@property
	def version(self):
		return clg.linkgrammar_get_version()

class ParseOptions(object):
	def __init__(self):
		self._po = clg.parse_options_create()
	
	def __del__(self):
		print "Deleting",self.__class__
		if self._po is not None:
			clg.parse_options_delete(self._po)
			self._po = None

class Dictionary(object):
	def __init__(self,lang):
		self._dict = clg.dictionary_create_lang(lang)
	
	def __del__(self):
		print "Deleting",self.__class__
		if self._dict is not None:
			clg.dictionary_delete(self._dict)
			self._dict = None
			
class Sentence(object):
	
	def __init__(self,s):
		self.s = s
		self._sent = clg.sentence_create(s,lp.dictionary._dict)
	
	def __del__(self):
		print "Deleting",self.__class__
		if self._sent is not None:
			clg.sentence_delete(self._sent)
			#print "Calling sentence_delete will cause a segfault"
			self._sent = None

	def parse(self):
		self.num_links = clg.sentence_parse(self._sent,lp.parse_options._po)
		return self.num_links

class Linkage(object):
	def __init__(self,idx,sentence):
		self.idx = idx
		self.sent = sentence
		self._link = clg.linkage_create(idx,sentence._sent,lp.parse_options._po)
		
	def __del__(self):
		print "Deleting",self.__class__
		if self._link is not None:
			clg.linkage_delete(self._link)
			self._link = None
		
	def print_diagram(self):
		print clg.linkage_print_diagram(self._link)
		
	def get_diagram(self):
		return clg.linkage_print_diagram(self._link)
		
def cleanup():
	print "Cleaning up linkgrammar..."

atexit.register(cleanup)


	

