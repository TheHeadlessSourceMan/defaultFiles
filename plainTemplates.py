"""
This is the set of available plain templates
"""
import os


class PlainTemplates(object):
	"""
	This is the set of available plain templates
	"""

	# TODO: need a better place to keep this because it certainly doesn't belong
	# in the python egg install directory!
	# DIRECTORY=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'plainTemplates'
	DIRECTORY=r'C:\backed_up\computers\programming\defaultFiles\plainTemplates'

	def __init__(self):
		pass

	@staticmethod
	def getTemplate(name):
		"""
		get a template by name
		"""
		for f in os.listdir(PlainTemplates.DIRECTORY):
			shortName=f.rsplit('.',1)[0]
			if shortName==name or f==name:
				return PlainTemplate(f,shortName)
		return None

	@staticmethod
	def getTemplateNames():
		"""
		list the available template names
		"""
		ret=[]
		for f in os.listdir(PlainTemplates.DIRECTORY):
			ret.append(f)
		return ret


class PlainTemplate(object):
	"""
	A single plain template
	"""

	def __init__(self,filename,name):
		self.filename=filename
		self.name=name

	def getVariables(self):
		"""
		Return empty dict since there are no variables with plain templates
		"""
		return {}

	def getFirstFile(self):
		"""
		return the filename
		"""
		return self.filename

	def getDir(self):
		"""
		get the directory
		"""
		d=PlainTemplates.DIRECTORY+os.sep+self.filename
		print d
		return d

	def shouldIgnore(self,file):
		"""
		Whethere this value should be ignored
		(always False for plain templates)
		"""
		return False

	def modifyFiles(self,atPath,variables):
		"""
		replace all variables in the atPath
		"""
		pass # no modification needed for plain templates

	def open(self,atPath,variables):
		"""
		Does nothing for plain templates
		"""
		pass # no auto-open on plain templates (user must open it manually)
