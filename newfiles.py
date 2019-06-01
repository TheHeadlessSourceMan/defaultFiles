#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Creates new files based on templates.
"""
import os
import tempfile
import shutil
from tkVarsWindow import runVarsWindow

from squareTemplates import SquareTemplates
from plainTemplates import PlainTemplates
from pythonTemplates import PythonTemplates


class NewFiles:
	"""
	Creates new files based on templates.

	TODO:
		Templates can be a zipped/tarred file (like an openoffice file)
		Templates can also be a directory with a bunch of templates inside
	"""

	ALL_TEMPLATES_CLASSES=[PythonTemplates,SquareTemplates,PlainTemplates]

	def __init__(self,templateName,prependNew=True):
		"""
		prependNew previxes new files with "new".
			e.g. template "webpage.html" creates "new webpage.html"
		"""
		self.prependNew=prependNew
		self.templateName=templateName
		self.template=None
		for c in self.ALL_TEMPLATES_CLASSES:
			self.template=c.getTemplate(templateName)
			if self.template is not None:
				break
		if self.template is None:
			raise Exception('ERR: Template "'+templateName+'" not found')

	def _createWorkspace(self):
		"""
		creates a new workspace for the current template

		returns the filesystem location of the temporary workspace
		"""
		tmpDir=tempfile.gettempdir()+os.sep+'newfiles'
		if os.path.isdir(tmpDir):
			shutil.rmtree(tmpDir)
		else:
			os.makedirs(tmpDir)
		#shutil.copytree(self.template.getDir(),tmpDir) # doesn't work right
		self._copyTree(self.template.getDir(),tmpDir)
		return tmpDir

	def _deleteWorkspace(self):
		"""
		if user cancells the process, delete the current workspace
		"""
		tmpDir=tempfile.gettempdir()+os.sep+'newfiles'
		if os.path.isdir(tmpDir):
			shutil.rmtree(tmpDir)

	def _copyTree(self,fromLocation,toLocation,currentPath=''):
		"""
		Copy an entire tree of files from one location to another
		"""
		if os.path.isdir(fromLocation):
			if not os.path.isdir(toLocation):
				os.makedirs(toLocation)
			for _,dirs,files in os.walk(fromLocation):
				for f in files:
					#print fromLocation+os.sep+currentPath+f,toLocation+os.sep+currentPath+f
					if not self.template.shouldIgnore(currentPath+f):
						shutil.copy2(fromLocation+os.sep+currentPath+f,toLocation+os.sep+currentPath+f)
				for d in dirs:
					#print fromLocation+os.sep+currentPath+d,toLocation+os.sep+currentPath+d
					childPath=currentPath+'d'
					if not self.template.shouldIgnore(childPath):
						self._copyTree(fromLocation+os.sep+currentPath+d,toLocation+os.sep+currentPath+d,childPath)
		else:
			filename=fromLocation.rsplit(os.sep,1)[-1]
			#print fromLocation,'>>',toLocation+os.sep+filename
			shutil.copy2(fromLocation,toLocation+os.sep+filename)

	def _saveWorkspace(self,toLocation):
		"""
		if user decides to approve, save the workspace to a location of their choosing
		"""
		if os.path.isfile(toLocation):
			# just in case they specified a filename, select the containing directory
			toLocation=toLocation.rsplit(os.sep,1)[0]
		elif not os.path.isdir(toLocation): # directory does not exist.  we must create items
			os.makedirs(toLocation)
		tmpDir=tempfile.gettempdir()+os.sep+'newfiles'
		#shutil.copytree(tmpDir,toLocation)
		self._copyTree(tmpDir,toLocation)
		self._deleteWorkspace() # clean up after ourselves

	def create(self,atLocation,**kwArgs):
		"""
		atLocation is where to create the new file(s)

		if other args are present, will assign them to variables
		otherwise will run the ui and ask for the variables
		"""
		workspace=self._createWorkspace()
		variables=self.template.getVariables()
		if variables:
			if kwArgs:
				for k,v in list(kwArgs.items()):
					variables[k].value=v
				worked=True # like the dialog was accepted (if we showed one)
			else:
				title='NEW '+self.templateName
				worked=runVarsWindow(variables,title)
		else:
			worked=True
		if worked:
			self.template.modifyFiles(workspace,variables)
			self._saveWorkspace(atLocation)
		else:
			self._deleteWorkspace()
		self.template.open(atLocation,variables)


if __name__ == '__main__':
	import sys
	# Use the Psyco python accelerator if available
	# See:
	# 	http://psyco.sourceforge.net
	try:
		import psyco
		psyco.full() # accelerate this program
	except ImportError:
		pass
	if len(sys.argv)<3:
		print('USEAGE:')
		print('   newfiles templateName location [arg=val,...]')
		print('where if no values are specified, it will bring up the ui')
	else:
		template=sys.argv[1]
		location=sys.argv[2]
		# stupid hoops to make it work with Windoze context menus
		if os.sep=='\\' and 'ComSpec' in os.environ:
			compath=os.environ['ComSpec'].rsplit('\\',1)[0]
			if os.getcwd()==compath: # we are being called from the comspec path
				# that means windoze probably sent us a directory AND whatever is selected within
				# so we need to go up a level
				location=location.rsplit('\\',1)[0]
		print('Template:',template)
		print('Location:',location)
		if len(sys.argv)>3:
			kwArgs={}
			for a in sys.argv[3:]:
				a=[x.strip() for x in a.split('=',1)]
				if len(a)>1:
					kwArgs[a[0]]=a[1]
				else:
					kwArgs[a[0]]='true'
			n=NewFiles(template,**kwArgs)
		else:
			n=NewFiles(template)
		n.create(location)