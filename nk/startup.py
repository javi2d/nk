

from contextlib import contextmanager

import nuke
import mdl
import nk
import inspect

"""Funciones de carga"""

INIT = []
MENU = []

__mod__ = mdl.uber.uberModule()

'decorator'
def init( fun ):

	item = ( inspect.getmodule( fun ) , fun.__name__ )
	if item not in __mod__.INIT:
		__mod__.INIT.append( item )
	return fun

def consume_inits():
	for mod,name in __mod__.INIT:
		print '@init: %s of %s' % ( name , mod )
		getattr( mod , name )()


'decorator'
def menu( fun ):

	item = ( inspect.getmodule( fun ) , fun.__name__ )
	if item not in __mod__.MENU:
		__mod__.MENU.append( item )	
	return fun

def consume_menus():
	for mod,name in __mod__.MENU:
		print '@init: %s of %s' % ( name , mod )
		getattr( mod , name )()




def load_plugins( path , addToSysPath=False , recursive = False ):

	path = mdl.shell( path , delegated = True )
	assert path.ISDIR

	for P,D,F in path.WALK:

		D[:] = [ d for d in D if not d.startswith('_') ] 

		nuke.pluginAddPath( P , addToSysPath=addToSysPath )
		if not recursive: return


def load_commands( root ):
	root = mdl.shell( root , delegated = True )
	nk.cmd.load_commands( root )


def flush_commands():
	nk.cmd.flush_commands()


def load_nodes( pattern ):

	items = mdl.shell( pattern , delegated = True ).GLOB
	for path in items:
		assert path.ISFILE , path
		nk.nscript.register_nscript( path )

	#nk.node.load( path('*.node.py') )	

def refresh():

	nk.cmd.reload_commands()
	nk.node.reload_nodes()		






