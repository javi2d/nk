


import nuke
import mdl

print '\n-> medula/mdl/nuke/__init__.py'

'Global Variables'

'nombre del knob de separacion'
CTRL_NAME = 'END_OF_USER_KNOBS_2014'

'True cuando el nodo esta en proceso de reconstruccion'
IN_BUILD_PROCESS   = False 


OPTIMIZE_CALLBACKS = True
BYPASS_CALLBACKS   = False
ACTIVE_CALLBACKS   = {}


'Temporal que nos indica la clase real del nodo que se crea userNode y userPanel'
'en build y callback, la de build se puede eleminar casi seguro'
TMP_USER_CLASS = None


'Usado tb en callbacks'
REAL_PANEL_NODES = {}
SINGLETON_PANELS = {}


'Almacen de listas de nscripts por clase'
'Usada en build.py , callback.py y aqui'
USER_CLASSES = {}
UCLS_LAST_KNAMES = {}



#import publish

import cmd
import build

import callback

import node

import nscript
import knobs

import This
'una instancia dinamica de This'
this = This()

import match
import startup
import execute
import taskbar
import selected

'para poder cargar menu.py de este directorio, carga los callbacks solo en menu'
nuke.pluginAddPath( mdl.shell( './startup_loaders' ) )






