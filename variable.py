"""
Tracks each variable and its changes throughout the system
"""


class Variable:
	"""
	Tracks each variable and its changes throughout the system
	"""
	def __init__(self):
		self.name=""
		self.description=""
		self.uitype="'text'" # an html input type like (checkbox color date
			# datetime datetime-local email file hidden image month number
			# password radio range search tel text time url week )
		self.value=""
		self.preReplace=""
		self.__needsEval__=True

	def evalPreReplace(self,localValues=None):
		"""
		evaluate the variable/code prior to replacing the values
		"""
		if self.preReplace:
			if localValues is None:
				localValues=[]
			v=self.preReplace
			#print '==='
			#print v
			#print '==='
			code='preReplace='+v
			try:
				exec(code,globals(),localValues)
				self.value=localValues['preReplace']
			except Exception as e:
				print(code)
				raise e

	def eval(self,localValues=None):
		"""
		evaluate the variable values code
		(except for preReplace)
		"""
		if self.__needsEval__:
			self.__needsEval__=False
			if localValues is None:
				localValues=[]
			for k in ['name','description','uitype','value']:
				v=getattr(self,k)
				if v:
					code=k+'='+v
					#print '==='+k+'===\n'+code+'\n\n'
					if k in localValues:
						old=localValues[k]
					else:
						old=None
					try:
						exec(code,globals(),localValues)
					except Exception as e:
						print(code)
						raise e
					#print '==='+k+'===\n'+str(localValues[k])+'\n\n'
					setattr(self,k,localValues[k])
					if old is not None:
						localValues[k]=old
					else:
						del localValues[k]

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

	def __repr__(self):
		return str(self.value)

	def __bool__(self):
		# this doesn't seem to work right with python.
		# must call toBool directly!
		return self.toBool()
	def toBool(self):
		"""
		use the variable as a bool
		"""
		s=self.__repr__()
		return len(s)>0 and (s[0] in 'YyTt1')