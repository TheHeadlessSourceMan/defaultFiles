#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Register windows explorer extensions
"""
try:
	import winreg
except ImportError:
	import _winreg as winreg
import os

from k_runner import pyErrRun

from squareTemplates import SquareTemplates
from plainTemplates import PlainTemplates
from pythonTemplates import PythonTemplates
ALL_TEMPLATES_CLASSES=[PythonTemplates,SquareTemplates,PlainTemplates]

HERE=os.path.abspath(__file__).rsplit(os.sep,1)[0]

# NOTE: the hierarchy of folders goes:
# (obviously not stored in registry like this)
#   *
#     Folder
#       Drive
#       Directory

# registry constants for the folder icon context menu
FOLDER_CONTEXT_MENU_TITLE='New From Template'
FOLDER_CONTEXT_MENU_FILETYPE='Folder' # 'AllFilesystemObjects' #'Directory'
FOLDER_CONTEXT_MENU_ID='newTemplate_menu' #'folderCtxTemplate_menu'
FOLDER_CONTEXT_MENU_ANCHOR_ID='folderCtxTemplate_anchor'

# registry constants for fiddling with the explorer background context menu
EXPLORER_BACKGROUND_MENU_TITLE=FOLDER_CONTEXT_MENU_TITLE
EXPLORER_BACKGROUND_MENU_FILETYPE='Directory' # I don't think this works anywhere but Directory
EXPLORER_BACKGROUND_MENU_ID=FOLDER_CONTEXT_MENU_ID#'explorerBkgTemplate_menu'
EXPLORER_BACKGROUND_MENU_ANCHOR_ID='explorerBkgTemplate_anchor'

ICON_PATH=HERE+os.sep+'list-add-4.ico'

# if you don't want a default icon for unknown types, set to None
UNKNOWN_ICON_PATH=HERE+os.sep+'lightbulb.ico'


def _nextShellNewName(extensionkey):
	"""
	create a shellnew name
	(currently does nothing)
	"""
	return 'ShellNew.1'


def registerToFile(templateName):
	"""
	templateName must have extension

	TODO: windows only allows one "new" per extension.  Perhaps make some kind of
	selector ui??

	NOTE: I had to do a full restart to make this work.  Is there a better way??

	See also:
		http://mc-computing.com/WinExplorer/WinExplorerRegistry_ShellNew.htm
	NOTE:
		besides the things listed, there are also
		Handler = CLSID
		IconPath = path
		ItemName = new item name
		MenuText = whatever
		Config->DontRename = ???
	"""
	extension='.'+templateName.rsplit('.',1)[1]
	try:
		extensionkey=OpenKey(HKEY_CLASSES_ROOT,extension)
	except WindowsError,e:
		print e
		extensionkey=CreateKey(HKEY_CLASSES_ROOT,extension)
	# todo: follow the default value and get a new key
	# create or open ShellNew
	try:
		key=OpenKey(extensionkey,'ShellNew')
		# since it is present:
		#	1) copy it to ShellNew.N
		newkey=CreateKey(extensionkey,_nextShellNewName(extensionkey))
		#	2) create a ShellNew.N+1 for the new stuff below
		newkey=CreateKey(extensionkey,_nextShellNewName(extensionkey))
		#	3) point original ShellNew to multimenu.py
	except WindowsError,e2:
		if str(e2).find('[Error 2]')>=0: # did not find the key, so create it
			try:
				newkey=CreateKey(key,'ShellNew')
			except WindowsError,e2:
				if str(e2).find('[Error 5]')>=0:
					print e2
					raise Exception('Did you forget to run as administrator?')
				else:
					raise e2
		else:
			raise e
	#cmd='cmd /k python.exe'
	cmd='python.exe "'+pyErrRun.getLocation()+'"'
	cmd=cmd+' "'+HERE+'newfiles.py" "'+templateName+'" "%v"'
	SetValue(key,'Command',REG_SZ,cmd)
	SetValue(key,'NullFile',REG_SZ,cmd) # not sure how necessary this is
	FlushKey(key)


def getAllNames():
	"""
	Gets all the template names in alphabetical order
	"""
	names=[]
	for c in ALL_TEMPLATES_CLASSES:
		names.extend(c.getTemplateNames())
	names.sort()
	return names


def getSystemIcon(forFile):
	"""
	get the sysem icon for a file type
	"""
	ext='.'+forFile.rsplit('.',1)[-1]
	icon=None
	try:
		key=winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,ext,0,winreg.KEY_READ)
		try:
			icon=winreg.QueryValue(key,'DefaultIcon')
		except WindowsError:
			pass
		next=winreg.QueryValue(key,None)
		#print ext,'->',next
		key=winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,next,0,winreg.KEY_READ)
		try:
			icon=winreg.QueryValue(key,'DefaultIcon')
		except WindowsError:
			pass
	except WindowsError,e:
		print e
	return icon

def getFirstTemplateFile(templateName):
	"""
	get the template file
	"""
	filename=None
	for c in ALL_TEMPLATES_CLASSES:
		template=c.getTemplate(templateName)
		if template!=None:
			break
	if template!=None:
		filename=template.getFirstFile()
	return filename

def getTemplateIcon(templateName):
	"""
	get the system icon for the template
	"""
	filename=getFirstTemplateFile(templateName)
	if filename!=None:
		return getSystemIcon(filename)
	return None

def unregisterFolderContextMenu(deep=True):
	"""
	a deep unregister removes everything, whereas the opposite
	removes only all your templates
	"""
	key=winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,FOLDER_CONTEXT_MENU_FILETYPE)
	if deep:
		winreg.DeleteKey(key,'Shell/'+FOLDER_CONTEXT_MENU_ANCHOR_ID)
	try:
		winreg.DeleteKey(key,FOLDER_CONTEXT_MENU_ID)
	except Exception:
		pass

def registerFolderContextMenu():
	"""
	register all shell new items we can provide with the individual folder right-click

	(Since we don't have an associated file type, we can't use New> so
	add everything to our own context menu instead)
	"""
	unregisterFolderContextMenu(False)
	key=winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,FOLDER_CONTEXT_MENU_FILETYPE)
	# create the anchor
	subkey=winreg.CreateKey(key,'Shell\\'+FOLDER_CONTEXT_MENU_ANCHOR_ID)
	winreg.SetValueEx(subkey,'ExtendedSubCommandsKey',0,winreg.REG_SZ,
		FOLDER_CONTEXT_MENU_FILETYPE+'\\'+FOLDER_CONTEXT_MENU_ID)
	winreg.SetValueEx(subkey,'MUIVerb',0,winreg.REG_SZ,FOLDER_CONTEXT_MENU_TITLE)
	winreg.SetValueEx(subkey,'Icon',0,winreg.REG_SZ,ICON_PATH)
	# create the context-submenu
	subkey=winreg.CreateKey(key,FOLDER_CONTEXT_MENU_ID)
	subkey=winreg.CreateKey(subkey,'Shell')
	# populate the submenu
	names=getAllNames()
	n=0
	for name in names:
		print 'Registering',name
		keyname='%03dcmd'%n
		#cmd='cmd /k python.exe'
		cmd='python.exe "'+pyErrRun.getLocation()+'"'
		cmd=cmd+' "'+HERE+os.sep+'newfiles.py" "'+name+'" "%v"'
		submenuKey=winreg.CreateKey(subkey,keyname)
		winreg.SetValueEx(submenuKey,'MUIVerb',0,winreg.REG_SZ,name)
		icon=getTemplateIcon(name)
		if icon is None and UNKNOWN_ICON_PATH!=None:
			icon=UNKNOWN_ICON_PATH
		if icon!=None:
			winreg.SetValueEx(submenuKey,'Icon',0,winreg.REG_SZ,icon)
		#winreg.SetValueEx(submenuKey,'NoWorkingDirectory',0,winreg.REG_SZ,'')
		submenuKey=winreg.CreateKey(submenuKey,'command')
		winreg.SetValueEx(submenuKey,None,0,winreg.REG_SZ,cmd)
		n+=1

def unregisterExplorerBackgroundMenu(deep=True):
	"""
	a deep unregister removes everything, whereas the opposite
	removes only all your templates
	"""
	key=winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,EXPLORER_BACKGROUND_MENU_FILETYPE)
	if deep:
		winreg.DeleteKey(key,'background\\Shell\\'+EXPLORER_BACKGROUND_MENU_ANCHOR_ID)
	try:
		winreg.DeleteKey(key,EXPLORER_BACKGROUND_MENU_ID)
	except Exception:
		pass

def registerExplorerBackgroundMenu():
	"""
	register all shell new items we can provide with the explorer window background right-click

	(Since we don't have an associated file type, we can't use New> so
	add everything to our own context menu instead)
	"""
	unregisterExplorerBackgroundMenu(False)
	key=winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,EXPLORER_BACKGROUND_MENU_FILETYPE)
	# create a background context menu anchor
	subkey=winreg.CreateKey(key,'Background\\shell\\'+EXPLORER_BACKGROUND_MENU_ANCHOR_ID)
	winreg.SetValueEx(subkey,'ExtendedSubCommandsKey',0,
		winreg.REG_SZ,EXPLORER_BACKGROUND_MENU_FILETYPE+'\\'+EXPLORER_BACKGROUND_MENU_ID)
	winreg.SetValueEx(subkey,'MUIVerb',0,winreg.REG_SZ,EXPLORER_BACKGROUND_MENU_TITLE)
	winreg.SetValueEx(subkey,'Icon',0,winreg.REG_SZ,ICON_PATH)
	# create the context-submenu
	subkey=winreg.CreateKey(key,EXPLORER_BACKGROUND_MENU_ID)
	subkey=winreg.CreateKey(subkey,'Shell')
	# populate the submenu
	names=getAllNames()
	n=0
	for name in names:
		print 'Registering',name
		keyname='%03dcmd'%n
		# NOTE: the explorer backgroun command uses "current working directory", whereas folders use %1
		#cmd='cmd /k python.exe'
		cmd='python.exe "'+pyErrRun.getLocation()+'"'
		cmd=cmd+' "'+HERE+os.sep+'newfiles.py" "'+name+'" "%V"'
		submenuKey=winreg.CreateKey(subkey,keyname)
		winreg.SetValueEx(submenuKey,'MUIVerb',0,winreg.REG_SZ,name)
		icon=getTemplateIcon(name)
		if icon is None and UNKNOWN_ICON_PATH!=None:
			icon=UNKNOWN_ICON_PATH
		if icon!=None:
			winreg.SetValueEx(submenuKey,'Icon',0,winreg.REG_SZ,icon)
		#winreg.SetValueEx(submenuKey,'NoWorkingDirectory',0,winreg.REG_SZ,'')
		submenuKey=winreg.CreateKey(submenuKey,'command')
		winreg.SetValueEx(submenuKey,None,0,winreg.REG_SZ,cmd)
		n+=1


if __name__ == '__main__':
	import sys
	import win32com.shell.shell as shell
	if False:
		ASADMIN = 'asadmin'
		# run this elevated
		if sys.argv[-1] != ASADMIN:
			script = os.path.abspath(sys.argv[0])
			params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
			shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
			sys.exit(0)
	#unregisterFolderContextMenu()
	#unregisterExplorerBackgroundMenu()
	registerFolderContextMenu()
	registerExplorerBackgroundMenu()
