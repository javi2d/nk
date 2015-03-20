


'operaciones inmediatas sobre los nodos seleccionados'

import nuke
import mdl

__mod__ = mdl.uber.uberModule()

def offset( x , y ):
	for node in nuke.selectedNodes():
		node.setXYpos( node.xpos() + x  , node.ypos() + y )





