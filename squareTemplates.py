
"""
A square template uses simple files marked up with [name,default,descr]
"""
import os
import re
from variable import *


class SquareTemplates(object):
	"""
	All of the installed square templates
	"""

	DIRECTORY=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'squareTemplates'

	def __init__(self):
		pass

	@staticmethod
	def getTemplate(name):
		"""
		get the template of the given name
		"""
		return None

	@staticmethod
	def getTemplateNames():
		"""
		list all of the template names
		"""
		# TODO: only populate this once the thing is working
		return []


class SquareTemplate(object):
	"""
	A square template uses simple files marked up with [name,default,descr]
	"""

	def __init__(self,name):
		self.name=name
		self.squareFinderRegex=r"""\[\[\s*(?P<name>.*?)\s*(?:\,\s*(?P<default>.*?)\s*(?:\,\s*(?P<desc>.*?)\s*)?)?\]\]"""
		self.squareFinderRegex=re.compile(self.squareFinderRegex)

	def getVariables(self):
		"""
		get all of the editable variables
		"""
		return {}

	def shouldIgnore(self,filename):
		"""
		if this template should ignore the file
		"""
		return False

	def getDir(self):
		"""
		get the directory
		"""
		return SquareTemplates.DIRECTORY+os.sep+self.name

	def create(self,atLocation):
		"""
		create the result of the template
		"""
		self._traverseFiles(atLocation,self._replaceVarsCB,context=None)

	def _findVarsCB(self,filename,f,context):
		"""
		walker tool to find variables
		"""
		data=f.read()
		for match in self.squareFinderRegex.finditer(data):
			name=match.group('name')
			if name is None:
				continue
			default=match.group('default')
			if default is None:
				default=''
			desc=match.group('desc')
			if desc is None:
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
			if name is None:
				continue
			default=match.group('default')
			if default is None:
				default=''
			desc=match.group('desc')
			if desc is None:
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
		"""
		replace variables in a filename
		"""
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
		if filename is None:
			original=True
			filename=''
			if self.prependNew:
				filename=filename+'new '
			filename=filename+self.templateName.rsplit(os.sep,1)[-1]
			self.variables['filename']=(filename,'new file to create')
		if templateFilename is None:
			templateFilename=SquareTemplates.DIRECTORY+os.sep+self.templateName
		# do a sweep for square variables
		self._traverseFiles(templateFilename,self._findSquareVarsCB,None)
		# run the ui
		print 'variables=',self.variables
		if original:
			app=VarsWindow('Values',self.variables)
			app.run()