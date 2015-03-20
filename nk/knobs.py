

import sys
import ast
import traceback
from contextlib import contextmanager
import types
import inspect
import threading
import time

import mdl
import nuke
import nk

def __init__( self ):

	'Esto ocurre la primera vez que se genera el uberModulo'

	class Virtual_Knob( object ):

		def __init__( self , cls ):
			self.__protoclass__ = cls
		def __call__( self, *args , **kwargs ):
			return __mod__.Proto_Knob( self.__protoclass__ , *args , **kwargs ) 
		def __repr__( self ):
			return "<Virtual_Knob('%s') at %s>" % ( self.__protoclass__ , hex(id(self)) )

	'POPULATE KNOBS'

	for cls in [ k for k in  vars( nuke ).keys() if k.endswith( '_Knob' ) ] + ['PythonKnob']:
		setattr( nk , cls , Virtual_Knob( cls ) )

	mdl.log.info( 'mdl module populated with nuke virtual knobs' )


def __call__( self, obj ):
	'Esto no hace nada. Sirve para marcar la estructura de knobs en los nscripts'
	return obj


__mod__ = mdl.uber.uberModule() 


######  ######  ####### ####### #######    #    # #     # ####### ######  
#     # #     # #     #    #    #     #    #   #  ##    # #     # #     # 
#     # #     # #     #    #    #     #    #  #   # #   # #     # #     # 
######  ######  #     #    #    #     #    ###    #  #  # #     # ######  
#       #   #   #     #    #    #     #    #  #   #   # # #     # #     # 
#       #    #  #     #    #    #     #    #   #  #    ## #     # #     # 
#       #     # #######    #    #######    #    # #     # ####### ######  


class Proto_Knob(object):

	#value = None , 

	def __init__( self, cls, label = None , value = None , flags = '' , clearflags = '' , tooltip = None ): #*args , **kwargs ): *args 
		
		assert isinstance(cls,str)
		self.Class = getattr( nuke , cls )
		assert issubclass( self.Class , nuke.Knob )
		
		self.label = label
		self.value = value
		self.flags = flags
		self.clearflags = clearflags
		self.tooltip = tooltip
		self.postcalls = []

		'Prueba de generacion de knobs'
		

	def __getattr__( self , att ):

		method = getattr( self('') , att , None )
		if method:
			def wrap( *args , **kwargs ):
				self.postcalls.append( (att,args,kwargs) )
				return self
			return wrap

		return object.__getattr__( self , att )


	def __call__( self , name ):

		try:
			knob = __mod__.create_real_knob( self , name )
		except:
			tb = mdl.uber.format_exception()
			error = '%s\nError durante la creacion del knob real desde el protoKnob' % tb
			error = mdl.net.html('font', error , size = 4, color = 'Crimson' ) 
			knob = nuke.Text_Knob( 'ERROR' , name , error )
			print error

		return knob



def create_real_knob( self, name ):

		label = name if self.label == None else self.label

		if self.value == None:
			knob = self.Class( name , label )
		else:
			knob  = self.Class( name , label , self.value )

		for flag in [ f.strip() for f in self.clearflags.split() if f.strip() ]:
			knob.clearFlag( getattr( nuke, flag ) )

		for flag in [ f.strip() for f in self.flags.split() if f.strip() ]:
			knob.setFlag( getattr( nuke, flag ) )

		for att,args,kwargs in self.postcalls:
			method = getattr( knob , att )
			method( *args , **kwargs )
		
		return knob



def compute_knobs( path ):

	path  = mdl.shell( path , delegated = True )

	'Hacer cache para que esto no se evalue dos veces'

	def resolve_partial( struct ):

		for item in struct:

			if isinstance( item , tuple ):
				tabname , content = item
				#print 'tab:' , tabname
				#if not content: continue
				PARENTS.append( tabname )
				PARTIAL.append( '[' )
				if not tabname.startswith( '_' ):
					tab = nuke.Tab_Knob( tabname , tabname )
					PARTIAL.append( tab )
				
					#tab.setVisible( False ) 
				resolve_partial( content )
				PARTIAL.append( ']' )
				PARENTS.pop()

			else:
				#print 'knob:' , item
				'regular knob, find PKnob in context'
				cur = MODULE
				for name in PARENTS + [item]:
					cur = getattr( cur , name )
				
				if type(cur).__name__ == 'Proto_Knob':
					pknob = cur
					'new knob generation, el knob de error se genera en "create_real_knob"'
					knob = pknob( name )
					PARTIAL.append( knob )

				elif isinstance( cur , types.ClassType ):
						
					'vamos a enganiar a inspect'

					sys.modules['__mod__'] = MODULE

					try:
						print inspect.getsourcelines( cur )
					except:
						raise
					finally:
						del sys.modules['__mod__']


	def resolve_knobs( PARTIAL ):

		KNOBS = []
		prev = None

		for k in PARTIAL:
			if k == '[':
				if prev == ']':
					KNOBS.pop()
				else:
					KNOBS.append( nuke.BeginTabGroup_Knob( None ) )
			elif k == ']':
				KNOBS.append( nuke.EndTabGroup_Knob( None ) )
			else:
				KNOBS.append( k )
			prev = k

		return KNOBS	


	PARTIAL = []
	PARENTS = []
	MODULE  = path.MOD


	'estructura del ast'
	STRUCT = __mod__.Names( path )
	resolve_partial( STRUCT )
	KNOBS = resolve_knobs( PARTIAL )
	return KNOBS[1:-1]

#	try:
#		
#	except:
#		traceback.print_exc()	
#		err_msg = mdl.net.html('font', traceback.format_exc(), 3, 'Crimson' ) 
#		KNOBS = [ nuke.Text_Knob( 'ERROR' , 'Error in Ast' , err_msg ) ]
#
#	finally:
#		
	




#     #    #    #     # #######  #####  
##    #   # #   ##   ## #       #     # 
# #   #  #   #  # # # # #       #       
#  #  # #     # #  #  # #####    #####  
#   # # ####### #     # #             # 
#    ## #     # #     # #       #     # 
#     # #     # #     # #######  #####  

                                   

class Names( ast.NodeVisitor ):

	'En esta nueva version debe devolver una lista anidada estructural de nombres'

	'[ (name,[]) , name , ]'

	'get a list of fullnames from classes from a source file'
	'resolucion de orden de knobs y tabs'

#	CACHE = {} #la carga doble puede ser por esto y el ubermodule

	def __new__( cls , path ):

		sh = mdl.shell( path , delegated = True )

		cache = mdl.uber.dictCache( 'knobs.Names' )

		stats,struct = cache.setdefault( sh , (None,None) )

		if stats != sh.STATS:
			
			'restaurar'
			self = super( Names,cls).__new__(cls)
			
			self.struct = []
			self.level  = 0

			node = ast.parse( sh.READ , sh , 'exec' )
			self.visit( node )

			cache[ sh ] = ( sh.STATS , self.struct )

			struct = self.struct

		return struct


	def visit_ClassDef( self , node ):

		if self.level == 0:
			decos = node.decorator_list
			'este deco esta definido como uberCallable de este modulo'
			if not decos or 'knobs' not in [d.attr for d in decos ]:
				return

		parent = self.struct
		self.struct = []

		parent.append( ( node.name , self.struct ) )
		self.level  += 1
		self.generic_visit( node )
		self.level  -= 1
		self.struct = parent

	def visit_Assign( self , node ):

		if self.level == 0:
			return

		for _node in node.targets:

			if type( _node ) == ast.Attribute:
				continue
			
			elif type( _node ) == ast.Name:
				self.struct.append( _node.id )

			elif 'elts' in _node._fields:
				'multiple asignacion' 
				self.struct += [ n.id for n in _node.elts ]			
			
			else:
				'solo aplican asignaciones con nombre'
				continue

	