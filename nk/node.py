

import sys

import mdl
import nuke
import nukescripts
import nk

import callback

from contextlib import contextmanager


__mod__ = mdl.uber.uberModule()


def userDagPos():

	selected = nuke.selectedNodes()
	n = nuke.createNode( 'Dot' )
	pos = n.xpos(),n.ypos()
	nuke.undo()
	[n.setSelected(True) for n in selected ]
	return pos





@contextmanager
def tmpUserClass( uclass ):
	'Usado por los UNode y UPanle creators'
	nk.TMP_USER_CLASS = uclass
	print 'DEBUG: USER_CLASS temporally set to : ' , uclass
	try:
		yield
	except: 
		raise
	finally:
		nk.TMP_USER_CLASS = None


#def storePanelNode( node ):
#
#	'Real panel node storage'
#	if isinstance( node, nuke.Node ):
#		if node.name() == 'PanelNode' and nk.TMP_USER_CLASS:
#			'solo se almacena si esta definida la variable nk.TMP_USER_CLASS'
#			nk.REAL_PANEL_NODES[ nk.TMP_USER_CLASS ] = node
#			mdl.log.debug( '~ real panel stored for class: %s' % nk.TMP_USER_CLASS	)



def addControlKnob( node ):

	ctrl = node.knobs().get( nk.CTRL_NAME , None )

	if not ctrl:
		ctrl = nuke.String_Knob(  nk.CTRL_NAME , 'uclass' , '' )
		node.addKnob( ctrl )
	
	ctrl.setFlag( nuke.INVISIBLE | nuke.DISABLED | nuke.EXPAND_TO_WIDTH | nuke.ENDLINE )
	if mdl.uber.DEVMODE: ctrl.clearFlag( nuke.INVISIBLE )

	ctrl.setValue( nk.TMP_USER_CLASS or ctrl.value() )	

	return ctrl



def safeNode( node = None ):

	'Current context node resolution'
	node = node or nuke.thisNode()
	try: 
		knobs = node.knobs()['name']
	except ValueError: 
		#mdl.log.warn( '~ A PythonObject is not attached to a node' )
		return None
	except: 
		raise
	else:
		return node

def realNode( node = None ):

	node = node or __mod__.safeNode( node )

	if node:

		if isinstance( node, nuke.PanelNode ):
			'mirar si tiene knob de control'
			ctrl = node.knobs().get( nk.CTRL_NAME , None )
			ucls = ctrl.value() if ctrl else None

			if ucls and ucls in nk.REAL_PANEL_NODES:
				node = nk.REAL_PANEL_NODES[ ucls ]
				#print 'Switching nuke.PanelNode for nuke.Node'
			else:
				node = None

	return node


def nodePanel( node = None ):

	node = node or __mod__.realNode( node )

	if node:
		ucls = node[ nk.CTRL_NAME ].value()
		return nk.SINGLETON_PANELS.get( ucls , None )		










def userNode( nodeClass , userClass , *args , **kwargs ):

	print '\nCreating userNode [%s] based on [%s]\n' % ( nodeClass , userClass )
	with __mod__.tmpUserClass( userClass ):
		if nodeClass == 'PanelNode':
			return __mod__.userPanel( userClass , *args , **kwargs )

		node = nuke.createNode( nodeClass , *args , **kwargs )
		node.setName( userClass )
		return node


def userPanel( userClass , title = None , scrollable = True , singleton = True , enabled = True ): #, data = None ):
	
	'Pobar a reciclar el nodo en las nuevas clases'

	panel  = nk.SINGLETON_PANELS.get( userClass , None )

	if not singleton or not panel:

		class CustomPanel( nukescripts.PythonPanel ):

			def __init__( self  ):
				nk.SINGLETON_PANELS[ userClass ] = self
				super(CustomPanel,self).__init__( title or userClass , userClass , scrollable )
				self.setEnabled( enabled )
				print 'Panel recien creado con enabled=' , self.isEnabled()

			def destroy( self ):
				self.close()
				super(CustomPanel,self).destroy()
				del nk.SINGLETON_PANELS[ userClass ]




		with __mod__.tmpUserClass( userClass ):
			print 'Creating new PythonPanel instance "%s"' % userClass
			panel = CustomPanel() # title or userClass , userClass , scrollable
			
			#print dir(panel)
			panel.node = nk.node.realNode( getattr(panel,'_PythonPanel__node') )
		
		#if singleton and old_panel:
		#	old_panel.close()
		#	old_panel.destroy()

	return panel




