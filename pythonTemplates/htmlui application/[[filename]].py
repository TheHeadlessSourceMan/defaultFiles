#!/usr/bin/python
import os
from htmlui import *

ui=HtmlUI()
# add html-callable functions here, such as: ui.addRemoteFunction(myFunction,'myFunction')
requirements=[]
exitCode=ui.run('[[filename]].html',requirements=requirements)
os._exit(exitCode) # os._exit() is used to take down all threads (normal exit() would block forever!)