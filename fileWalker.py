import os
import zipfile,tarfile
import io

SKIP_EXTENSIONS=['exe','dll','pdb','msi','sys','gif','jpg','jpeg','png','bmp','mp3','qtw','mp4','wav','mid','bmp','obj','com','cpl','xcf','psd','pyc','pyo','pyd','iso','a','o','flv','m4a','so','ttf','fon','pch','wmv']

class FileWalker:
	"""
	walks a set of files and gives you a chance to edit them at will
	
	The advanced part of this is that you can traverse compressed files as well!
	
	Will traverse all combinations of directories, files, 
		zip, 7z, gzip, bzip, and tar files
		
	TODO: Tar stuff is untested
	TODO: 7z zip stuff is not finished
	"""
	def __init__(self,location,skipExtensions=SKIP_EXTENSIONS,debug=False):
		"""
		location can be a filename, list, or open file handle
		"""
		self.location=location
		self.skipExtensions=skipExtensions
		self.debug=debug
		
	def getVariables(self):
		return []
		
	def traverse(self,dataCB,context=None):
		"""
		dataCB is in the form fn(filename,filehandle,context)
		if dataCB returns None, it keeps going
		but if it returns anything else, the traversal stops
		
		where context is any object you want
		"""
		return self._traverseFiles('',self.location,dataCB,context)
		
	def _debug(self,message):
		if self.debug:
			print 'FILEWALKER:',message
		
	def _shouldWalk(self,filename):
		if self.skipExtensions!=None:
			filename=filename.rsplit('.',1)
			if len(filename)>1:
				if filename[-1].lower() in self.skipExtensions:
					self._debug('skipping '+('.'.join(filename)))
					return False
		return True

	def _traverseFiles(self,path,location,dataCB,context=None):
		"""
		path and location are identical for a regular filesystem, but are different
		if you start traversing into compressed files:
			path=c:\foo\bar\baz.html, location=c:\foo\bar\baz.html
			path=c:\foo.zip\bar\baz.html, location=\bar\baz.html
		"""
		ret=None
		if type(location)==list:
			self._debug('[list]')
			# Go though a list of files
			for s in location:
				ret=self._traverseFiles(path,s,dataCB,context)
				if ret!=None:
					break
		elif type(location)==str:
			# it is a file name
			if not self._shouldWalk(location):
				pass
			elif os.path.isdir(location):
				# is is a directory
				self._debug('[dirname] '+path)
				for root,dirs,files in os.walk(location):
					for subdir in files:
						subdir=root+os.sep+subdir
						ret=self._traverseFiles(subdir,subdir,dataCB,context)
						if ret!=None:
							break
					if ret!=None:
						break
					for subdir in dirs:
						subdir=root+os.sep+subdir
						ret=self._traverseFiles(subdir,subdir,dataCB,context)
						if ret!=None:
							break
					if ret!=None:
						break
					if ret!=None:
						break
			else:
				# it is a regular file, so open it and try again
				self._debug('[filename] '+location+' '+path)
				f=open(location,'rb')
				ret=self._traverseFiles(location,f,dataCB,context)
				f.close()
		else:
			filename=''
			if hasattr(location,'name'):
				filename=location.name
			if self._shouldWalk(filename):
				# make it seekable
				if False:#not location.seekable(): # make sure we have something we can do random access on
					f2=io.BytesIO() # create a new file in a memory buffer
					f2.write(location.read())
					location.close()
					location=f2
					location.seek(0) # be kind, rewind
				# check if it is a tar file
				try: # unfortunately, the only way to tell if its a tar from a filehandle is to try and read it
					tf=tarfile.open(fileobj=location,mode="r:")
					isTar=True
				except Exception,e:#tarfile.READ_ERROR:
					#print 'Archive error',e
					isTar=False
					pass
				if isTar:
					self._debug('[file] Tar '+path)
					for name in tf.getmembers():
						if self._shouldWalk(name):
							f=tf.extract(name)
							ret=self._traverseFiles(path+os.sep+name,f,dataCB,context)
							f.close()
							if ret!=None:
								break
				elif location.read(2)=='7z':
					raise ImplementationError()
				elif zipfile.is_zipfile(location):
					try:
						location.seek(0)
					except io.UnsupportedOperation:
						pass # zip files do not allow seeking
					# is it a zip file?
					self._debug('[file] Zip '+path)
					zf=zipfile.ZipFile(location)
					for name in zf.namelist():
						if self._shouldWalk(name):
							f=zf.open(name)
							ret=self._traverseFiles(path+os.sep+name,f,dataCB,context)
							f.close()
							if ret!=None:
								break
				else:
					# it must be a regular file object
					self._debug('[file] '+path)
					if self._shouldWalk(filename):
						try:
							location.seek(0)
						except io.UnsupportedOperation:
							pass # zip files do not allow seeking
						ret=dataCB(path,location,context)
		return ret
		
		
if __name__ == '__main__':
	import sys
	
	def myCB(filename,fileHandle,context):
		print filename
	
	if len(sys.argv)<2:
		print 'USEAGE: fileWalker.py filename(s)'
	else:
		fw=FileWalker(sys.argv[1:],None)
		fw.traverse(myCB,None)