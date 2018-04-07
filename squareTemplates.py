import os
import re
from variable import *


class SquareTemplates:
	DIRECTORY=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'squareTemplates'
	
	def __init__(self):
		pass
		
	@staticmethod
	def getTemplate(name):
		return None
	
	@staticmethod
	def getTemplateNames():
		# TODO: only populate this once the thing is working
		return []
		
class SquareTemplate:
	def __init__(self,name):
		self.name=name
		self.squareFinderRegex=r"""\[\[\s*(?P<name>.*?)\s*(?:\,\s*(?P<default>.*?)\s*(?:\,\s*(?P<desc>.*?)\s*)?)?\]\]"""
		self.squareFinderRegex=re.compile(self.squareFinderRegex)
		
	def getVariables(self):
		return {}
		
	def shouldIgnore(self,file):
		return False
		
	def getDir(self):
		return SquareTemplates.DIRECTORY+os.sep+self.name
		
	def create(self,atLocation):
		self._traverseFiles(atLocation,self._replaceVarsCB,context=None)
		
	def _findVarsCB(self,filename,f,context):
		data=f.read()
		for match in self.squareFinderRegex.finditer(data):
			name=match.group('name')
			if name==None:
				continue
			default=match.group('default')
			if default==None:
				default=''
			desc=match.group('desc')
			if desc==None:
				desc=''
			if self.variables.has_key(name):
				# fill in any desc/default if missing
				dd=self.variables[name]
				if dd[0]=='' and default!='':
					if dd[1]=='' and desc!='':
						self.variables[name]=(default,desc)
					else:
						self.variables[name]=(default,dd[1])
				elif dd[1]=='' and desc!='':
					self.variables[name]=(dd[0],desc)
			else:
				self.variables[name]=(default,desc)
		for match in self.squareFinderRegex.finditer(filename):
			name=match.group('name')
			if name==None:
				continue
			default=match.group('default')
			if default==None:
				default=''
			desc=match.group('desc')
			if desc==None:
				desc=''
			if self.variables.has_key(name):
				# fill in any desc/default if missing
				dd=self.variables[name]
				if dd[0]=='' and default!='':
					if dd[1]=='' and desc!='':
						self.variables[name]=(default,desc)
					else:
						self.variables[name]=(default,dd[1])
				elif dd[1]=='' and desc!='':
					self.variables[name]=(dd[0],desc)
			else:
				self.variables[name]=(default,desc)
		
		
	def _replaceVarsCB(self,filename,f,context):
		data=f.read()
		for name,value in self.variables.items():
			regex=r"""(\[\[\s*"""+re.escape(name)+r"""((?:\s|\,).*?)?\]\])"""
			data=re.sub(regex,value[0].replace('\\','\\\\'),data)
		f.seek(0)
		f.write(data)
		
		

	def _editVariables(self,atLocation,templateFilename=None,filename=None):
		"""
		format for tags is [[name,default,description]]
		
		templateFilename and filename are used internally.  Do not change them.
		"""
		template=None
		original=False
		if filename==None:
			original=True
			filename=''
			if self.prependNew:
				filename=filename+'new '
			filename=filename+self.templateName.rsplit(os.sep,1)[-1]
			self.variables['filename']=(filename,'new file to create')
		if templateFilename==None:
			templateFilename=SquareTemplates.DIRECTORY+os.sep+self.templateName
		# do a sweep for square variables
		self._traverseFiles(templateFilename,self._findSquareVarsCB,None)
		# run the ui
		print 'variables=',self.variables
		if original:
			app=VarsWindow('Values',self.variables)
			app.run()