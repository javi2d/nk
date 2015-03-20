


'''
Modulo para la reconstruccion de nodos (incluidos paneles) usando el api de nodescript

'''


import itertools

import nuke
import sys
from contextlib import contextmanager
import threading
import time

import mdl
import nk
#__all__ = ['build_node']

__mod__ = mdl.uber.uberModule()


########  ##     ## #### ##       ########  
##     ## ##     ##  ##  ##       ##     ## 
##     ## ##     ##  ##  ##       ##     ## 
########  ##     ##  ##  ##       ##     ## 
##     ## ##     ##  ##  ##       ##     ## 
##     ## ##     ##  ##  ##       ##     ## 
########   #######  #### ######## ########  



def build_node( node , values = None , force_rebuild = False ):

	'Esta funcion reconstruye el nodo si o si'

	real_node = nk.node.realNode( node )
	assert real_node , 'Solo se pueden reconstruir nodos de tipo nuke.Node : %s' % repr( node )

	ctrl = real_node.knobs().get( nk.CTRL_NAME , None )
	assert ctrl , 'No se pueden reconstruir nodos sin knob de control : %s' % repr( node )

	'Reconstruye si se fuerza o si hay cambios en la estructura de nombre '
	if force_rebuild or __mod__.name_struct_changed( real_node ):
		
		'El nodo no se toca si no se ofrece nada para la reconstrucion'
		valid_classes = ( nk.USER_CLASSES.get( real_node.Class() , None ) , nk.USER_CLASSES.get( ctrl.value() , None ) )
		if any( valid_classes ):
			__mod__.fill_node( real_node , values )





 ######  ##     ## ########  ########   #######  ########  ######## 
##    ## ##     ## ##     ## ##     ## ##     ## ##     ##    ##    
##       ##     ## ##     ## ##     ## ##     ## ##     ##    ##    
 ######  ##     ## ########  ########  ##     ## ########     ##    
      ## ##     ## ##        ##        ##     ## ##   ##      ##    
##    ## ##     ## ##        ##        ##     ## ##    ##     ##    
 ######   #######  ##        ##         #######  ##     ##    ##  




@contextmanager
def inBuild():

	'Usado por los UNode y UPanle creators'
	nk.IN_BUILD_PROCESS = True
	try: yield
	except: raise
	finally:
		nk.IN_BUILD_PROCESS = False





def name_struct_changed( node ):

	''

	new_knames = ','.join( nk.nscript.get_knames( node ) ) 		
	if not new_knames: return False

	cur_knames = ','.join( [ k.name() for k in node.allKnobs() ] )
	if cur_knames.endswith( ',' + new_knames ): return False

	return True




def clear_node( node ):

	if mdl.uber.DEVMODE:
		sys.__stdout__.write( '-> clearing node [%s]\n' % node.name() )	

	node = nk.node.realNode( node )
	assert nk.CTRL_NAME in node.knobs()

	ctrl_value = node.knobs()[ nk.CTRL_NAME ].value()

	values = node.writeKnobs( nuke.ALL | nuke.TO_SCRIPT |  nuke.WRITE_NON_DEFAULT_ONLY  ) #nuke.TO_VALUE |
	
	for k in reversed( node.allKnobs() ):
		try: 
			node.removeKnob( k )
		except: 
			mdl.log.debug( '\tError deleting Knob %s' % k )
		if k.name() == nk.CTRL_NAME: 
			break
	
	ctrl = nk.node.addControlKnob( node )
	ctrl.setValue( ctrl_value )

	if mdl.uber.DEVMODE:
		sys.__stdout__.write( '<- clearing node [%s]\n' % node.name() )	

	return values


def fill_node( node , values ):

	'SOLO usado por __mod__.build_node'
	if nk.IN_BUILD_PROCESS:
		'Mientras el nodo se reconstruye se desactivan los callbacks'
		return

	with __mod__.inBuild():

		node = nk.node.realNode( node )
		assert nk.CTRL_NAME in node.knobs()

		if mdl.uber.DEVMODE:
			sys.__stdout__.write( '-> filling node [%s]\n' % node.name() )		

		'Cuidado! nk.nscript.get_knobs es un iterador y solo funciona una vez'
		KNOBS = tuple( nk.nscript.get_knobs( node ) )

		'-> CLEAR NODE'
	
		cur_values = __mod__.clear_node( node )
		values = values or cur_values

		'-> FILL NODE'

		for k in KNOBS:

			cond_avoid_knob = isinstance( k , nuke.Tab_Knob ) and k.name() == 'User'

			if cond_avoid_knob:
				'Elimina el tab llamado User'
				continue

			'Elimina el knob si esta duplicado0'
			if k.name() in node.knobs():
				try: node.removeKnob( node.knobs()[k.name()] )
				except: mdl.log.error( 'Error deleting duplicated knob %s' % k )

			try:
				node.addKnob( k )
			except:
				err = str( sys.exc_info() )
				err_knob = nuke.Text_Knob( k.name() , k.label() , mdl.net.html('font', err , color = 'Red' )   )
				node.addKnob( err_knob )

			'Aqui nunca entra un tipo PanelNode, nodo es nuke.Node o deberia serlo, incluso los paneles'
			if node.Class() == 'PanelNode':
				k.setFlag( nuke.NO_UNDO | nuke.NO_ANIMATION )

		node.readKnobs( values )

		if mdl.uber.DEVMODE:
			sys.__stdout__.write( '<- filling node [%s]\n' % node.name() )		

#		if mdl.uber.DEVMODE:
#			
#			if not ucls:
#				msg = mdl.net.html('font','Custom User Class undefined.', color = 'LightGrey' )
#			elif ucls not in nk.USER_CLASSES:
#				msg = mdl.net.html('font', 'Custom User Class "%s" is undefined.' % ucls , color =  'Red' )
#			elif not KNOBS:
#				msg = mdl.net.html('font', 'No knobs defined by user classes.' , color =  'Orange' )
#			else:
#				msg = mdl.net.html('font', 'OK' , color =  'Green' )
#
#			node.knobs()[ 'REBUILD_STATUS' ].setValue( msg )		







