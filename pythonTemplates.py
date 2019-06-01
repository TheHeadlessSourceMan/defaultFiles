#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
A template system wherein python code can be embedded directly into
the template
"""
import os
import collections
from ezFs import *
from variable import *


ILLEGAL_FILENAME_CHARS=r'*"/:;|=,\\'
def _filenameFixer(filename):
	"""
	NOTE: be sure to ONLY include the filename, not a path
	"""
	for i in ILLEGAL_FILENAME_CHARS:
		if filename.find(i)>0:
			filename=filename.replace(i,'_')
	return filename


class PythonTemplates:
	"""
	A template system wherein python code can be embedded directly into
	the template
	"""

	# TODO: need a better place to keep this because it certainly doesn't belong
	# in the python egg install directory!
	#DIRECTORY=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep+'pythonTemplates'
	DIRECTORY=r'C:\backed_up\computers\programming\defaultFiles\pythonTemplates'

	def __init__(self):
		pass

	@staticmethod
	def getTemplate(name):
		"""
		get a python template by name
		"""
		if os.path.isfile(PythonTemplates.DIRECTORY+os.sep+name+os.sep+'template.ini'):
			return Template(name)
		return None

	@staticmethod
	def getTemplateNames():
		"""
		list all installed python templates
		"""
		ret=[]
		for f in os.listdir(PythonTemplates.DIRECTORY):
			if os.path.isfile(PythonTemplates.DIRECTORY+os.sep+f+os.sep+'template.ini'):
				ret.append(f)
		return ret

class Replace:
	"""
	Represents a replacement tag in the .ini
	"""

	def __init__(self):
		self.find=""
		self.replace=""
		self.files="'*'"
		self.__needsEval__=True

	def eval(self,localValues=None):
		"""
		evaluate the replacement as python code
		"""
		if self.__needsEval__:
			self.__needsEval__=False
			for k in ['find','replace','files']:
				v=getattr(self,k)
				if v:
					try:
						v=str(eval(v,localValues))
					except Exception as e:
						print('OOPS!  There seems to be something wrong with replacement variable "'+k+'"')
						print('   (Usually this is because you forgot to put it in quotes.)')
						raise e
					setattr(self,k,v)

	def __repr__(self):
		"""
		get a string representation of this replacement
		"""
		result=[]
		for k in ['find','replace','files']:
			v=getattr(self,k)
			result.append(k+'='+str(v))
		return '\n'.join(result)


class Template:
	"""
	A single python template
	"""

	def __init__(self,name):
		self.name=name
		self.replaces=[]
		self.variables=[]
		self.load(name)

	def getFirstFile(self):
		"""
		Get the first available filename
		"""
		ez=EzFs(self.getDir())
		filename=None
		for r in self.replaces:
			files=ez.glob(r.files)
			if files:
				filename=files[0]
				break
		return filename

	def getVariables(self):
		"""
		Get all the variable objects
		"""
		variables=collections.OrderedDict()
		for v in self.variables:
			variables['self']=self # reset every time in case something doesn't play nice
			v.eval(localValues=variables)
			variables[v.name]=v # add as we go, so later variables can build upon earlier
		for k,v in list(variables.items()):
			if not isinstance(v,Variable):
				print('"'+k+'" is not a variable.  Deleting.')
				del variables[k]
		return variables

	def __repr__(self):
		ret=[self.name]
		for k,v in list(self.getVariables().items()):
			ret.append('  '+k+'='+('\n    '.join(str(v.value).split('\n'))))
		return '\n'.join(ret)

	def shouldIgnore(self,filename):
		"""
		Whether this file should be ignored
		"""
		if filename=='template.ini':
			return True
		return False

	def getDir(self):
		"""
		get the directory
		"""
		return PythonTemplates.DIRECTORY+os.sep+self.name

	def load(self,name):
		"""
		load the template ini file
		"""
		self.name=name
		filename=PythonTemplates.DIRECTORY+os.sep+name+os.sep+'template.ini'
		f=open(filename,'r')
		current=None
		currentLine=[]
		for line in f:
			line=line.rstrip()
			line_s=line.lstrip()
			if (not line_s) or line_s[0]=='#':
				continue
			if line_s.startswith('[variable]'):
				current=Variable()
				self.variables.append(current)
			elif line_s.startswith('[replace]'):
				current=Replace()
				self.replaces.append(current)
			elif line_s.startswith('[stuff]'):
				current=self
			else:
				if line.endswith('\\'):
					currentLine.append(line[0:-1])
				else:
					currentLine.append(line)
					# bump indenting left so everything lines up with first line
					currentLine[0]=currentLine[0].strip()
					if len(currentLine)>1:
						indent=len(currentLine[1])-len(currentLine[1].lstrip())
						if currentLine[0][-1]==':': # see if we SHOULD be indented one
							indent=indent-1
						indent=currentLine[1][0:indent]
						for i in range(1,len(currentLine)):
							if currentLine[i].startswith(indent):
								currentLine[i]=currentLine[i][len(indent):]
					currentLine='\n'.join(currentLine)
					# now determine what value we are setting
					currentLine=[x.strip() for x in currentLine.split('=',1)]
					if len(currentLine)!=2 or not currentLine[1] or not hasattr(current,currentLine[0]):
						print('WARN: error parsing:',currentLine)
						#raise Exception()
					else:
						setattr(current,currentLine[0],currentLine[1])
					currentLine=[]

	def _replaceFileContents(self,ezFile,find,replace):
		"""
		replace the contents of a single file

		find can be a string or a compiled regular expression
			if it is a string, will try to replace both ascii and unicode strings in the file

		NOTE: does not change the file's name,  use _replaceFileName() for that
		"""
		isRe=False
		try:
			isRe=(find.__class__.__name__=='SRE_Pattern')
		except Exception:
			pass
		f=ezFile.open('rb')
		if f is None:
			print('ERR: Unable to find file\n'+ezFile.abspath)
		data=f.read(encoding=None) # this will return raw bytes
		f.close()
		if isRe:
			data=find.sub(replace,data)
		elif isinstance(find,str):
			data=data.replace(find.encode('utf-8'),replace.encode('utf-8'))
			try: # in case the file has wide character encoding
				data=data.replace(find.encode('UCS-2'),replace.encode('UCS-2'))
			except Exception:
				pass
		else:
			find=str(find)
			replace=str(replace)
			data=data.replace(find,replace)
			try:
				data=data.decode('utf-8')
				find=find.decode('utf-8')
				replace=replace.decode('utf-8')
				data=data.replace(find,replace)
			except Exception:
				pass
		f=ezFile.open('wb')
		f.write(data)
		f.close()

	def _replaceFileName(self,ezFile,find,replace):
		"""
		perform a replacement within the filename of a single file

		find can be a string or a compiled regular expression
			if it is a string, will try to replace both ascii and unicode strings in the file
		"""
		isRe=False
		try:
			isRe=(find.__class__.__name__=='SRE_Pattern')
		except Exception:
			pass
		newFilename=ezFile.name.rsplit(os.sep,1)
		if isRe:
			newFilename[-1]=find.sub(replace,newFilename[-1])
		elif isinstance(find,str):
			if isinstance(replace,bytes):
				replace=replace.encode('utf-8')
			if type(newFilename[-1])==type(find):
				newFilename[-1]=newFilename[-1].replace(find,replace)
			try:
				find=find.encode('ascii')
				replace=replace.encode('ascii')
				if type(newFilename[-1]==type(find)):
					newFilename[-1]=newFilename[-1].replace(find,replace)
			except Exception:
				pass
		else:
			find=str(find)
			replace=str(replace)
			if type(newFilename[-1]==type(find)):
				newFilename[-1]=newFilename[-1].replace(find,replace)
			try:
				find=find.encode('utf-8')
				replace=replace.encode('utf-8')
				if type(newFilename[-1]==type(find)):
					newFilename[-1]=newFilename[-1].replace(find,replace)
			except Exception:
				pass
		# now see if we need to rename it
		newFilename[-1]=_filenameFixer(newFilename[-1])
		newFilename=os.sep.join(newFilename)
		if ezFile.name!=newFilename:
			print('CHANGE FILENAME'+'"'+ezFile.name+'" to "'+newFilename+'"')
			ezFile.rename(newFilename)

	def _replaceFileWalker(self,ezFile):
		"""
		Walks through the files and does the replacement
		"""
		for r in self.replaces: # attempt every replacement on this file
			if ezFile.path not in r.files:
				print('IGNORED: find',r.find,'within',ezFile.path)
			else:
				print('VISITING: find',r.find,'upon',ezFile.path)
				if not isinstance(ezFile,BaseFsDirectory):
					self._replaceFileContents(ezFile,r.find,r.replace)
				# change the file name if necessary
				self._replaceFileName(ezFile,r.find,r.replace)

	def open(self,atPath,variables):
		"""
		open a path
		"""
		openAfter=''
		if 'openAfter' in variables:
			openAfter=variables['openAfter'].value
		if openAfter is not None and openAfter:
			cmd=None
			if openAfter.lower() in ['os','default']:
				# TODO: this only works on windows!
				program='start'
				for n in ['openThis','filename','directory']:
					if n in variables:
						cmd=program+' "'+str(variables[n].value)+'"'
						break
				import win32api
				atPath=os.path.abspath(atPath)
				_=win32api.ShellExecute(0,'open',atPath+os.sep+str(variables[n].value),None,atPath,0)
			else:
				code='openAfter="'+openAfter+'"'
				try:
					exec(code,globals(),variables)
				except Exception as e:
					print(code)
					raise e
				cmd=str(variables['openAfter'])
				if cmd is not None and cmd:
					import subprocess
					subprocess.Popen(cmd,shell=True)

	def modifyFiles(self,atPath,variables):
		"""
		replace all variables in the atPath
		"""
		if atPath[-1]!=os.sep:
			atPath=atPath+os.sep
		# pre-evaluate any variables with evalPreReplace attributes
		for k,v in list(variables.items()):
			if k!='self' and isinstance(v,Variable):
				variables['self']=self # reset every time in case something doesn't play nice
				v.evalPreReplace(variables)
		for k,v in list(variables.items()):
			if not isinstance(v,Variable):
				del variables[k]
		# make the variables into local values for using in scripts
		localDict={}
		for k,v in list(variables.items()):
			localDict[v.name]=v
		ez=EzFs(atPath)
		# get every Replace item ready for use
		for r in self.replaces:
			localDict['self']=self # reset every time in case something doesn't play nice
			r.eval(localValues=localDict)
			for k,v in list(localDict.items()):
				if k in variables:
					variables[k].value=v
			if isinstance(r.files,str):
				# if it is a string (glob expression), convert it into a list of files now
				if r.files is None or r.files=='*':
					# this is a special case meaning "everything", including all directories and subdirectories
					r.files=[f.path for f in ez.getAll()]
					r.files.append(ez.path)
				elif r.files.find('*')>=0 or r.files.find('?')>=0:
					r.files=[f.path for f in ez.glob(r.files)]
				else:
					r.files=[r.files]
				#print 'FILES IN SET:',r.files
		# do the replacement!
		ez.walk(self._replaceFileWalker,context=None,algo='DEAPTH-FIRST')


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
		print('   newfiles templateName location')
	else:
		print('Template:',sys.argv[1])
		print('Location:',sys.argv[2])
		n=Template(sys.argv[1])
		n.create(sys.argv[2])