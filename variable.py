import datetime

class Variable:
	def __init__(self):
		self.name=""
		self.description=""
		self.uitype="'text'" # an html input type like (checkbox color date datetime datetime-local email file hidden image month number password radio range search tel text time url week )
		self.value=""
		self.preReplace=""
		self.__needsEval__=True
		
	def evalPreReplace(self,locals=None):
		if self.preReplace!='':
			if locals==None:
				locals=[]
			v=self.preReplace
			code='preReplace='+v
			try:
				exec(code,globals(),locals)
				self.value=locals['preReplace']
			except Exception,e:
				print code
				raise e
		
	def eval(self,locals=None):
		"""
		evaluate the variable values code
		(except for preReplace)
		"""
		if self.__needsEval__:
			self.__needsEval__=False
			if locals==None:
				locals=[]
			for k in ['name','description','uitype','value']:
				v=getattr(self,k)
				if v!='':
					code=k+'='+v
					#print '==='+k+'===\n'+code+'\n\n'
					if locals.has_key(k):
						old=locals[k]
					else:
						old=None
					try:
						exec(code,globals(),locals)
					except Exception,e:
						print code
						raise e
					#print '==='+k+'===\n'+str(locals[k])+'\n\n'
					setattr(self,k,locals[k])
					if old!=None:
						locals[k]=old
					else:
						del locals[k]
		
	def __int__(self):
		return int(self.value)
		
	def __float__(self):
		return float(self.value)
		
	def __setattr__(self,k,v):
		if isinstance(v,Variable):
			# don't ever let a Variable in, but instead, copy its field.
			self.__dict__[k]=getattr(v,k)
		else:
			self.__dict__[k]=v
		
	def __str__(self):
		return str(self.value)
		
	def __bool__(self):
		# this doesn't seem to work right with python.
		# must call toBool directly!
		return self.toBool()
	def toBool(self):
		s=self.__str__()
		return len(s)>0 and (s[0] in 'YyTt1')