

import sys
import re

import mdl
import nuke

import time
import marshal

import itertools
import inspect

import mdl
import nk



'Como cuando cargamos un nscript generamos el listado de knobs podemos almacenar un string\
con los nombres '

__mod__ = mdl.uber.uberModule()



def register_nscript( path ):

	path = mdl.shell( path , delegated = True )
	
	'evaluacion del contexto'
	path.CTX



	uclasses = nk.USER_CLASSES.setdefault( path.TAGNAME , [] )
	if path not in uclasses: uclasses.append( path )
	
	'Generamos los knobs por si tienen algun error'
	__mod__.nscript_knobs( path )

	sys.__stdout__.flush()
	sys.__stdout__.write( '+nod -> %s\n' % path.BASENAME )

	

def unregister_nscript( path ):

	path = mdl.shell( path , delegated = True )
	uclasses = nk.USER_CLASSES.setdefault( path.TAGNAME , [] )
	if path in uclasses: uclasses.remove( path )

	sys.__stdout__.flush()
	sys.__stdout__.write( '-nod -> %s\n' % path.BASENAME )



def nscript_knobs( path ):

	'Lista de los knobs que genera individualmente un archivo nscript'

	path = mdl.shell( path , delegated = True )
	knobs = nk.knobs.compute_knobs( path )
	'almacenamos los ultimos knames buenos para comparativas futuras'
	nk.UCLS_LAST_KNAMES[ path ] = [ K for K in [ k.name() for k in knobs ] if K ]
	return knobs



def get_knobs( node ):

	'Suma de los knobs por node script'

	scripts = __mod__.get_node_scripts( node )
	knobs = itertools.chain( *( __mod__.nscript_knobs( path ) for path in scripts )  )
	return knobs

def get_knames( node ):

	'Suma de los nombres '

	KNAMES = nk.UCLS_LAST_KNAMES

	scripts = __mod__.get_node_scripts( node )
	knames = itertools.chain( *( KNAMES[ path ] for path in scripts if path in KNAMES )  )
	return knames


def nscript_tabs( path ):

	'Listado de '

	path = mdl.shell( path , delegated = True )

	'Devuelve un listado de nscripts definidos dentro del contexto del actual archivo'

	ctx = path.CTX if mdl.uber.DEVMODE else vars( path.MODULE )
	
	tabs = ctx.get( 'TABS' , [] )

	if isinstance( tabs , str ):
		tabs = [ i.strip() for i in re.split( ',|;| ' , tabs ) if i.strip() ]
	assert isinstance( tabs , (tuple,list) )

	'Genera el listado de paths (scripts) definidos por TABS'

	scripts = []

	for t in tabs:
		tab_scripts = nk.USER_CLASSES.get( t , None )
		if not tab_scripts:
			print 'WARNING: Invalid TAB value "%s" in %s' % ( t , path.BASENAME )
			continue
		[ scripts.append(s) for s in tab_scripts if s not in scripts ]

	if path not in scripts:
		scripts.insert(0,path)	

	return scripts


def get_node_scripts( node ):

	'Dado un nodo devuelve los paths (scripts) que afectan al nodo'

	this = nk.This( node )		
	
	uclasses = this.CLS, this.UCLS #this.GET_CONTROL_VALUE 

	scripts = []

	for cls in uclasses:
		for path in nk.USER_CLASSES.get( cls,[] ):
			tabs = [ scrpt for scrpt in __mod__.nscript_tabs( path ) if scrpt not in scripts ]
			scripts += tabs

	return scripts


def get_callbacks( node , name ):

	scripts = __mod__.get_node_scripts( node )

	callbacks = []

	for path in scripts:
		ctx = path.CTX if mdl.uber.DEVMODE else vars( path.MODULE )
		if name in ctx:
			callbacks.append( ctx[name] )

	return callbacks



















#
#
#class NScript(object):
#
#	'''Carga archivos .node.py que representa una estructura 
#	de knobs y callbacks que se puede aplicar a cualquier nodo
#	'''
#
#	def __init__( self , path ):
#
#		self.path  = mdl.shell( path , delegated = True )
#
#		'pre cache del contexto'
#		self.path.CTX
#
#		self.name = self.path.TAGNAME
#
#		self.timestamp = time.time()
#
#		uclasses = nk.USER_CLASSES.setdefault( self.name , [] )
#
#		'Comprobacion de duplicidad'
#		paths = [ns.path for ns in uclasses]
#		if self.path not in paths:
#			uclasses.append( self )
#	
#		mdl.log.info( '+node -> %s' % path.BASENAME )
#
#		self.knames = []
#		self.knobs()
#		'ESTO estaba un tab menos'
#		'por si el fichero presenta problemas'
#		'Generamos los knobs del ns, tb se evalua el modulo como efecto colateral'
#
#
#	def __repr__(self):
#		return "<NScript '%s' object at %s>" % ( self.path.TAGNAME , hex(id(self)) )
#
#	def knobs( self ):
#
#		knobs = nk.knobs.generate_knobs( self )
#		self.knames = [ K for K in [ k.name() for k in knobs ] if K ]
#		return knobs
#
#	def tabs( self ):
#
#		'Devuelve un listado de nscripts definidos dentro del contexto del actual archivo'
#
#		ctx = self.path.CTX if mdl.uber.DEVMODE else vars( self.path.MODULE )
#		
#		tabs = ctx.get( 'TABS' , [] )
#
#		if isinstance( tabs , str ):
#			tabs = [ i.strip() for i in re.split( ',|;| ' , tabs ) if i.strip() ]
#
#		assert isinstance( tabs , (tuple,list) )
#
#		scripts = []
#
#		for t in tabs:
#			tab_scripts = nk.USER_CLASSES.get( t , None )
#			if not tab_scripts:
#				print 'WARNING: Invalid TAB value "%s" in %s' % ( t , self.path.BASENAME )
#				continue
#			[ scripts.append(s) for s in tab_scripts if s not in scripts ]
#
#		if self not in scripts:
#			scripts.insert(0,self)	
#
#		return scripts
#
#
#	'no, pq las funciones pueden estar definidas en archivos externos'
#
#
#

