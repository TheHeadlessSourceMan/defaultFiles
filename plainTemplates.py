import os

class PlainTemplates:
	# TODO: need a better place to keep this because it certainly doesn't belong 
	# in the python egg install directory!
	# DIRECTORY=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'plainTemplates'
	DIRECTORY=r'C:\backed_up\computers\programming\defaultFiles\plainTemplates'
	
	def __init__(self):
		pass
		
	@staticmethod
	def getTemplate(name):
		for f in os.listdir(PlainTemplates.DIRECTORY):
			shortName=f.rsplit('.',1)[0]
			if shortName==name or f==name:
				return PlainTemplate(f,shortName)
		
	@staticmethod
	def getTemplateNames():
		ret=[]
		for f in os.listdir(PlainTemplates.DIRECTORY):
			ret.append(f)
		return ret
		
class PlainTemplate:
	def __init__(self,filename,name):
		self.filename=filename
		self.name=name
		
	def getVariables(self):
		return {}
		
	def getFirstFile(self):
		return self.filename
		
	def getDir(self):
		d=PlainTemplates.DIRECTORY+os.sep+self.filename
		print d
		return d
		
	def shouldIgnore(self,file):
		return False
		
	def modifyFiles(self,atPath,variables):
		"""
		replace all variables in the atPath
		"""
		pass # no modification needed for plain templates
		
	def open(self,atPath,variables):
		pass # no auto-open on plain templates (user must open it manually)
	