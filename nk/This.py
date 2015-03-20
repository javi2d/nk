
import sys
import nuke
import threading

import mdl
import nk


def __call__( self , *args , **kwargs ):
	
	#getattr( __mod__ , '@' )
	#__mod__.__name__
	
	__mod__.__reload__

	return __mod__.This( *args , **kwargs )


__mod__ = mdl.uber.uberModule()

__reload__ = None


class This(object):
	
	__metaclass__ = mdl.uber.uberClass

	def __init__( self , node=None, knob=None ):

		if isinstance( node , str ):
			node = nuke.toNode( node )
		
		self.__node__ = node

		if isinstance( knob , str ):
			knob = self.KNOBS[knob]	

		self.__knob__ = knob

	def __str__( self ):

		nname = self.NODE.name() if self.NODE else None
		kname = self.KNOB.name() if self.KNOB else None

		if kname:
			return "This( '%s','%s',%s )" % ( nname , kname , repr(self.VALUE) )
		else:
			return "This( '%s' )" % nname

	def __getattr__( self , att ):

		'para evaluar metodos sin parametros utilizando la forma mayuscula'
		'ins.method(self) -> ins.METHOD'

		if att.isupper():
			att = att.lower()
			'Esta es la forma de convertir una clase en ineractiva'
			_method = getattr( __mod__.This , att ).__get__( self , This )
			return _method()
		 
		return object.__getattribute__( self , att )


	def root( self ):
		root = nuke.root()
		return root



	def safe_node( self ):
		return nk.node.safeNode( self.__node__ )

	'* valor real'
	def node( self ):
		return nk.node.realNode( self.__node__ )


	def panel( self ):
		return nk.node.nodePanel( self.__node__ )



	def proxy_mode( self ):
		return self.ROOT['proxy'].value()

	def script_name( self ):

		root_path = self.ROOT['name'].value()
		return mdl.shell( root_path ) if root_path else root_path


	'Classes'

	def cls( self ):
		node = self.SAFE_NODE
		ncls = 'PanelNode' if isinstance( node, nuke.PanelNode ) else node.Class()
		return ncls	

	def ucls( self ):
		node  = self.NODE
		ctrl  = node.knobs().get( nk.CTRL_NAME , None )
		value = ctrl.value() if ctrl else None
		return value


	'* valor real'
	def knob( self ):
		return self.__knob__ or nuke.thisKnob() if self.NODE else None

	'* valor real'
	def value( self ):
		return self.KNOB.value()

	def name( self ):
		'REVISE: node.name ( en root no es lo mismo )' 
		return self.VALUES['name']
		'en root esto no es lo mismo que Root.name()'



	def kname( self ):
		return self.KNOB.name()


	def knobs( self ):
		ctx = [ (n,k) for n,k in self.NODE.knobs().iteritems() ] #)dict( 
		uber = mdl.uber.uberObject() << ctx
		return uber


	def values( self ):

		ctx = [ (n,k.value()) for n,k in self.NODE.knobs().iteritems() ] #)dict( 
		uber = mdl.uber.uberObject() << ctx
		return uber 


	def write( self ):

		return self.NODE.writeKnobs( nuke.ALL | nuke.TO_SCRIPT | nuke.TO_VALUE  )  

	def write_changed( self ):
		return self.NODE.writeKnobs( nuke.ALL | nuke.TO_SCRIPT | nuke.TO_VALUE | nuke.WRITE_NON_DEFAULT_ONLY  )

	def ff( self ):

		return self.NODE.firstFrame()

	def lf( self ):

		return self.NODE.lastFrame()

	def frange( self ):
		'repr del frame range del nodo'
		return str( self.NODE.frameRange() )

	def pattern( self ):
		'patron ACTIVO normalizado del reader'
#		pattern = mdl.shell( self.NODE['file'].value() ).REPLACE_HASHES
#		return pattern

		knames = ['file','proxy']
		'mirar esto si se espera el path del proxy'
		if nuke.root().proxy(): knames = reversed( knames )

		node = self.NODE

		for kname in [ kn for kn in knames if kn in node.knobs() ]:
			patt = node[kname].value().strip()
			if patt: 
				return mdl.shell( patt ).REPLACE_HASHES	



	def frames( self ):
		'Lista de frames del nodo'
		if '%' in self.PATTERN:
			frames = range( self.NODE.firstFrame() , self.NODE.lastFrame()+1 )
		else:
			frames = [ None ]
		return frames

	def length( self ):
		return len( self.FRAMES )


	def set_focus( self , knob = None ):

		if knob==None: 
			k = self.KNOB
		elif isinstance( knob , str ):
			k = self.KNOBS[knob]
		else:
			k = knob

		assert k
		k.setFlag(0)


	def selected( self ):

		class selection:

			selection = nuke.selectedNodes()

			def __getattr__( self , att ):

				results = []
				for n in self.selection:
					result = This(n).__getattr__( att )
					results.append( result )
				return results

		return selection()


	def click_coords( self ):

		'User pos'	
		n = nuke.createNode('Dot')
		coords = n.xpos(),n.ypos()
		nuke.delete( n )
		return coords





#	def __getitem__( self , k ):



 

#	def static( self ):
#		return nk.This( self.NODE , self.KNOB )





#	def this_root( self ):
#		return nk.This( self.ROOT )




#	def real_node( self ):
#
#		return self.NODE
#
#		'En el caso de un nodo panel se recupera el nodo real'
#
#		node = self.NODE
#		assert node
#		ucls = self.UCLS
#
#		if isinstance( node, nuke.PanelNode ):
#			if ucls in nk.REAL_PANEL_NODES:
#				node = nk.REAL_PANEL_NODES[ ucls ]		
#
#		return node
#
#	def target_node( self ):
#
#		return self.NODE
#
#		'devuelve un nodo si este es adecuado para un callback'
#
#		node = self.NODE
#		
#		if not node: return
#
#		ucls = nk.TMP_USER_CLASS or self.GET_CONTROL_VALUE
#
#		if ucls==None: return
#
#		return self.REAL_NODE

	
#	def this_node( self ):
#		return nk.This( self.NODE ) if self.NODE else None


#	def this_knob( self ):
#		return nk.This( self.NODE , self.KNOB )





	'Ctrl'

#	def has_control_knob( self ):
#
#		'Get the ctrl knob if any'
#
#		node = self.NODE
#		assert node
#
#		return  nk.CTRL_NAME in node.knobs()
#
#	def get_control_knob( self ):
#
#		'Get the ctrl knob if any'
#
#		node = self.NODE
#		assert node
#		return node.knobs().get(  nk.CTRL_NAME , None )

#
#	def add_control_knob( self ):
#
#		'Add a ctrl knob if none is present'
#
#		node = self.NODE
#		assert node
#
#		if not self.HAS_CONTROL_KNOB:
#			k = nuke.String_Knob(  nk.CTRL_NAME , 'uclass' , '' )
#			k.setFlag( nuke.INVISIBLE | nuke.DISABLED | nuke.EXPAND_TO_WIDTH  )
#			k.setFlag( nuke.ENDLINE )
#			node.addKnob( k )
#		else:
#			k = self.GET_CONTROL_KNOB
#
#		if mdl.uber.DEVMODE:
#			k.clearFlag( nuke.INVISIBLE )
#
#		value = nk.TMP_USER_CLASS
#
#		if value:
#			k.setValue( value )
#
#		return k

#	def get_control_value( self ):
#
#		'Get value of ctrl knob if any'
#		ctrl_knob = self.GET_CONTROL_KNOB
#		'CUIDADO, este valor puede ser "" , y por lo tanto no se debe utilizar una booleana para comprobarlo '
#		return ctrl_knob.value() if ctrl_knob else None
#
#
#	def is_registered( self ):
#
#		node = self.REAL_NODE
#		assert node
#
#		if nk.TMP_USER_CLASS or node.Class() in nk.USER_CLASSES.keys():
#			return True
#		return False
#
#
	def clear_node( self ):

		return nk.build.clear_node( self.NODE )

	def rebuild( self ):

		nk.build.build_node( self.NODE )


	def force_rebuild( self ):

		nk.build.build_node( self.NODE , force_rebuild = True )

	
	
#	def clear_node( self ):
#		
#		node = self.REAL_NODE


#	def build_node( self ):
#
#		node = self.REAL_NODE
#
#		if nk.build.is_registered( node ):
#
#			nk.build.add_control_knob( node )
#			nk.build.build_node( node )
#



#		'Objeto panel en base al objeto nodo o en su defecto el ultimo panel'
#
#		result = [ p for n,p in reversed( mdl.NODE_PANEL_DICT ) if n == self.NODE ]
#		if result:
#			return result[0]
#		else:
#			return mdl.LAST_PANEL
#

#	def this_pnode( self ):
#		return nk.This( self.PNODE )
#
#
#
#	def this_panel( self ):
#		return nk.This( self.PANEL )	



#
#' FOCUS ahora esta en this' 
#
#
#def setFocus( knob ):
#	
#	assert isinstance( knob , nuke.Tab_Knob ) , 'Solo se puede hacer foco a Tabs'
#
#	#def task( knob ):
#	
#	def task( knob ):
#
#		node = knob.node()
#
#		mdl.log.info( 'Setting focus on tab : %s of %s' % ( knob.name() , node.name() ) )
#
#		if node == nuke.Root():
#			mdl.task.execInMainThreadWithResult( knob.clearFlag , nuke.INVISIBLE )
#			#knob.clearFlag( nuke.INVISIBLE )
#		else:
#			tabs = [ k for k in node.allKnobs() if isinstance( k , nuke.Tab_Knob ) ]	
#			idx = tabs.index( knob )
#			mdl.task.execInMainThreadWithResult( node.setTab , idx )
#
#	mdl.task.thread_daemon( task , knob ).start()
#
#	#mdl.task.execInMainThreadWithResult( knob.setFlag , nuke.INVISIBLE )
#	#mdl.task.execInMainThreadWithResult( knob.clearFlag , nuke.INVISIBLE )
#
	









