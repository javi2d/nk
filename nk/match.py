

"""
Ofrece una serie de funciones para selecciones de nodos

Hay que ampliar este modulo con seleciones por color, match de nombres de secuencias 
en los directorios que este la secuencia etc

"""

import nuke
import mdl

__mod__ = mdl.uber.uberModule()

def connected( nodes ):

	nodes = nodes[:]

	result = []
	while nodes:
		node = nodes.pop()
		result.append( node )
		deps = node.dependencies( nuke.INPUTS | nuke.HIDDEN_INPUTS | nuke.EXPRESSIONS ) #
		new = [ n for n in deps if n not in result + nodes ]
		nodes.extend( new )

	return result	


def select_connected( nodes ):

	nodes[0].selectOnly()
	cnodes = __mod__.connected( nodes )
	[ n.setSelected( True ) for n in cnodes ]
	return cnodes



#def dependent( nodes ):
#
#	nodes  = __mod__.connected( nodes )
#	result = []
#
#	for node in nodes:
#		dependent = n.dependent( nuke.EXPRESSIONS , forceEvaluate = True )
#		result.extend( dependent )
#	
#	return result
#
#	
#	print new
