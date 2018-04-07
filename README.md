---
title: default files
---

This is an tool quickly
create default files to get you started easily without the unnecessary
steps.  

There are three different template styles to choose from: A plain template where files are simply copied over.  A square bracket template where all variables are \[\[varname\]\], and a python template where you can replace whatever you want and execute arbitrary bits of code. 

plain templates
---------------
These are quick and simple \"copy this file\" templates. Just throw the
file in, run (as administrator) registerWinExplorer.bat and you\'re
done.

Such an obvious thing to do, yet it is strangely lacking from Windows.


square templates
----------------
An old idea to have an intermediate stage between plain templates and
pythonTemplates.

It is currently broken, and I don\'t know if I care to bring it back.


python templates
----------------
These allow for very rich and sophisticated templates to be written.
They achieve this by using simple variables that also allow embedding of
python snippets.

To create one, add a new directory under \"pythonTemplates\" with the
name of the template.

In this directory, add any replacement files and resources as well as a
template.ini file.

To install the template(s) into the system menu, run (as administrator)
registerWinExplorer.bat

python template.ini
-------------------
```ini
\[stuff\]\
    icon=\"\" \...\...\... TODO: the icon to display in the system menu
(you may want to add this to \"nocopy\" as well)\
    nocopy=\"\" \...\.... TODO: ignore certain files during copying\
\
\[variable\]\
    name=\"\" \...\...\... the name of the replacement (in ui)\
    description=\"\" .. Description of the replacement (ui tooltip)\
    uitype=\"\" \...\.... type of ui element (none,field,textarea,\...
more to come) (default=field)\
    value=\"\" \...\..... default value\
    preReplace=\"\" \... code to run after the vars window, but before
the replacement\
\
\[replace\]\
    find=\"\" \...\...\..... what to replace (usually something unique
like \[\[name\]\] is a good idea)\
replace=\"\" \...\..... what to replace it with\
    files=\[\"\"\] \...\..... which files to perform replacement in
(default=\*, meaning all files)\
\
\[ignore\]\
    files=\[\"\"\] \...\..... which files to not copy over (useful if
you have code in here) (default=\[\'template.ini\'\])\
```
Remember, everything on the right hand side of = is python code, so you
can do all kinds of useful and/or unfortunate things with this.\
\
If there are no variables that are not none, will not show the ui\
\
There is a special variable called openAfter that will cause an external
command to be run after the thing is created.\
You can set its value to \"os\" or \"default\" to use the system default
opener for this type.\
\
Any line can be commented out by beginning it with a \# character\
Python for all items is evaluated IN ORDER, so you may want to arrange
things based on any external changes they make

Known issues
------------

* square templates do not work - I don\'t know whether to bother anymore
since python templates are so much better

* replacements can be made to the filename, but after changing, the files
list becomes incorrect (for now, do this last)

how do I\...
------------
**Create a file programatically rather than from a template file?

Check out the \"png image\" template.

**Automatically open the file after it is created?

Set the special variable named \"openAfter\". You can either set this as
uitype=\"hidden\" or let the user change it.

**Not have a pop-up window?

Simply set all variables to uitype=\"hidden\"

**Validate or change the value type of a variable?

Use the preReplace value with some code, in the general form:\
preReplace=my\_convert(variable\_name.value)\
Check out the \"png image\" template.

**Have multiple lines of python?

Simply end each line with \\

**Access something from the \[stuff\] section in a script?

Use self. For example, \"self.icon\" works.

**Include an external python library?

With the python \"include\" statement as normal. NOTE: \"include \* from
x\" might not work. Rather, use the form \"include x\" and then
\"x.whatever()\"

**Execute code in a different order from what the ui is?

Order your variables according to the ui order, then add extra
uitype=\"hidden\" variables to do the processing you want.
