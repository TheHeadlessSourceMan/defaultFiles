# This is the setup info for the python installer.
# You probably don't need to do anything with it directly.
# Just run make and it will be used to create a distributable package
# for more info on how this works, see:
#	http://wheel.readthedocs.org/en/latest/
#	and/or
#	http://pythonwheels.com
from setuptools import setup, Distribution


class BinaryDistribution(Distribution):
    def is_pure(self):
        return True # return False if there is OS-specific files


if __name__ == '__main__':
	import sys
	import os
	here=os.path.dirname(os.path.realpath( __file__ ))
	sys.path.append(here) 
	name='defaultFiles'
	plainTemplates='plainTemplates'
	squareTemplates='squareTemplates'
	plainTemplatesName=name+'.'+plainTemplates
	squareTemplatesName=name+'.'+squareTemplates
	version='1.0'
	description='A tool for automatically creating new files based on templates.'
	packages=[name,plainTemplatesName,squareTemplatesName]
	package_data={ # add all files for a package
		name:[],
		plainTemplatesName:[],
		squareTemplatesName:[]
	}
	package_dir={name:here,plainTemplatesName:here+os.sep+plainTemplates,		squareTemplatesName:here+os.sep+squareTemplates}
	distclass=BinaryDistribution
	setup(name=name,version=version,description=description,packages=packages,package_dir=package_dir,package_data=package_data,distclass=distclass)
