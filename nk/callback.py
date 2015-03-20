

import os
import sys
import mdl
import nuke
import nk

import time
import threading
import inspect

LOCK = threading.RLock()

USER_CALLBACKS = {}



def __call__( self , args = tuple() , kwargs = {} , nodeClass = None ):
	return __mod__.callback( args , kwargs , nodeClass )


__mod__ = mdl.uber.uberModule()


def get_cbadder(cbname):
	'de esta forma tan generica es valido para versiones anteriores de nuke'
	return vars( nuke ).get( 'add' + cbname[0].upper() + cbname[1:] , None )


def callback( args = tuple() , kwargs = {} , nodeClass = None ):

	if inspect.stack()[1][3] == '__call__':
		path = inspect.stack()[2][1] #module path
	else:
		path = inspect.stack()[1][1] #module path

	basename = os.path.basename(path)

	#print 'fun %s is defined in %s' % ( cbname , basename )

	storage = __mod__.USER_CALLBACKS.setdefault( path , {} )	

	def callback_decorator( fun ):

		cbname  = fun.__name__

		print '\nuser callback -> %s : %s' % (basename , cbname)
		
		adder = vars( nuke ).get( 'add' + cbname[0].upper() + cbname[1:] , None )
		remover = vars( nuke ).get( 'remove' + cbname[0].upper() + cbname[1:] , None )

		if adder and remover:

			'arguments'
			if nodeClass == None:
				arguments = ( fun , args , kwargs )
			else:
				arguments = ( fun , args , kwargs , nodeClass )

			'Eliminando el antiguo'
			if cbname in storage:
				print '\tRemoving previous user callback -> %s : %s' % (basename , cbname)
				remover( *storage[cbname] )
				del storage[cbname]

			print '\tAdding user callback:', basename , cbname
			adder( *arguments )
			storage[cbname] = arguments

			def remove_callback():
				if cbname in storage:
					print 'Manually removing user callback -> %s : %s' % (basename , cbname)
					remover( *storage[cbname] )
					del storage[cbname]

			fun.remove_callback = remove_callback 

		return fun

	return callback_decorator


#mdl.uber.uberCallable( callback )

#def __callback__( fun ):
#	'el nombre de la funcion da el tipo de callback'
#	'solo uno de cada tipo por fichero'
#	return __mod__.callback( fun )









NODE_CALLBACKS = [ 'onScriptLoad', 'onScriptSave', 'onScriptClose',  
'afterRender', 'beforeRender', 'afterFrameRender', 'beforeFrameRender', 'renderProgress',
'onUserCreate', 'onDestroy', 'onCreate' , 'knobChanged' , 'autolabel' ] # ,'updateUI'

SPECIAL_CALLBACKS = [ 'afterBackgroundRender', 'afterBackgroundFrameRender',  'beforeBackgroundRender' ]

def create_callbacks():
	
	'''
	Antes de los callbacks ya deberiamos tener definidos y cargados los nodos
	Esto crea un CALLBACK GENERICO para los nodos por defecto por cada uno de los callbacks disponibles EXCEPTO KNOBCHANGED
	Depende de donde se la llame, funcionara o no en GUI MODE
	El callback KNOBCHANGED se agrega en el onCreate del Nodo
	'''

#	def add_callback( cbname , funct ): #, *args 
#		
#		cbadder = vars( nuke ).get( 'add' + cbname[0].upper() + cbname[1:] , None )
#		if cbadder:
#			cbadder( funct , args = (cbname,) )
#			mdl.log.info( '+cb -> %s' % cbname )
#	
	

	'Los launchers se crean por cuestiones de interactividad con el ubermodule'

	def panel_onCreate_launcher():
		def launch(): return __mod__.panel_onCreate()
		return launch

	def onCreate_launcher():
		def launch(): return __mod__.generic_onCreate()
		return launch

	def generic_launcher(cbname):
		def launch(): return __mod__.generic_callback(cbname)
		return launch
	
	def special_launcher(cbname):
		def launch(*args): return __mod__.generic_callback(cbname)
		return launch


	nuke.addOnCreate( onCreate_launcher() )

	nuke.addOnCreate( panel_onCreate_launcher() , nodeClass = 'PanelNode' )


	for cbname in __mod__.NODE_CALLBACKS:

		cbadder = __mod__.get_cbadder( cbname )
		if cbadder:

			cbadder( generic_launcher(cbname)  )

			sys.__stdout__.flush()
			sys.__stdout__.write( '+cbk -> %s\n' % cbname )

	for cbname in __mod__.SPECIAL_CALLBACKS:

		cbadder = __mod__.get_cbadder( cbname )
		if cbadder:
			cbadder( special_launcher(cbname) )
			sys.__stdout__.flush()
			sys.__stdout__.write( '+cbk (special) -> %s\n' % cbname )



def panel_onCreate():
	print 'Panel Created'
	pass


def generic_onCreate():

	'Este callback aplica a todos los tipos de nodo incluido el root'
	'Lo que hacemos es consolidar el nodo para que el sistema lo pueda procesar'
	'Aqui sienpre entra una instancia de nuke.Node, nunca de PanelNode'


	'Consolida el nodo para el sistema de callbacks y reconstruccion'

	node = nk.node.safeNode()

	'si el nodo es invalido lo ignora'
	if node:

		'Real panel node storage'
		if isinstance( node, nuke.Node ) and node.name() == 'PanelNode' and nk.TMP_USER_CLASS:
			
			'solo se almacena si esta definida la variable nk.TMP_USER_CLASS'
			nk.REAL_PANEL_NODES[ nk.TMP_USER_CLASS ] = node
			mdl.log.debug( '~ real panel stored for class: %s' % nk.TMP_USER_CLASS	)


		'Solo aplica esto a los nodos que hayan sido definidos'
		if nk.TMP_USER_CLASS or node.Class() in nk.USER_CLASSES.keys():
			
			'aplicacion del knob de control'
			nk.node.addControlKnob( node )



		'Aqui siempre es nodo real por lo que no hay que comprobarlo'

		ctrl = node.knobs().get( nk.CTRL_NAME , None )
		if ctrl:
			'si tiene knob de control se puede reconstruir'
			#print 'Reconstruccion en onCreate %s' % node.name()
			nk.build.build_node( node )	



def generic_callback( cbname ): 

	if __mod__.filter_callbacks( cbname ): return
	
	node = nk.this.NODE
	
	if not node: 
		'no se procesa si el nodo es invalido'
		return

	if nk.CTRL_NAME not in node.knobs():
		'no se peocesan los nodos sin knob de control'
		return

	if mdl.uber.DEVMODE:
		__mod__.log_callback( node , cbname )

	results = __mod__.consume_callbacks( node , cbname )

	'AUTOLABEL'

	if cbname == 'autolabel':

		'Sumatorio de todos los autolabel definidos'

		results = [ unicode(s) for s in  results if s ]

		if 'label' in node.knobs():
			user_label = node['label'].evaluate()
			if user_label and user_label.strip():
				results.append( user_label.strip() )

		if results:
			html_label = mdl.net.html( 'center' , '\n'.join( [ node.name() ] + results ) )
			return html_label




def temp_disable_knobChanged():

	'Deshabilita temporalmente el callback generico relativo a knobChanged'

	'No se si el Lock tiene efecto'

	src = nuke.knobChangeds['*']
	with __mod__.LOCK:
		tmp , src[:] = src[:] , []

	time.sleep(.5)

	if tmp:
		with __mod__.LOCK:
			src[:] = tmp
		print 'restored knob changed %s' % ( 'OK' if src else 'ERROR!, se han perdido los knob changed' )
			
		if not src:
			nuke.message( 'Se han perdido los knobChenge callbacks' )


	return True



def filter_callbacks( cbname ):

	if cbname=='knobChanged' and nuke.thisKnob().name() in ('xpos','ypos') and len( nuke.selectedNodes() ) > 1:
		
		if nuke.knobChangeds['*']:

			threading.Thread( None , __mod__.temp_disable_knobChanged ).start()	
			return True

	'bypass de redundancia, no se si esta activo'
	if nk.BYPASS_CALLBACKS: return True
	'Mientras el nodo se reconstruye se desactivan los callbacks'
	if nk.IN_BUILD_PROCESS: return True





def consume_callbacks( node , cbname ):


	callbacks = nk.nscript.get_callbacks( node , cbname )	

	if cbname == 'knobChanged':
		kname = nuke.thisKnob().name()
		callbacks += nk.nscript.get_callbacks( node , kname )

	results = []

	for cb in callbacks:

		result = cb()
		results.append( result )

		#try:
		#	
		#except:
		#	'SOFT traceback'
		#	import traceback
		#	'\n\t*'.join( traceback.format_exc().split('\n') )

	return results

def log_callback( node , cbname ):

	name = 'PanelNode' if isinstance( node , nuke.PanelNode ) else node.fullName() 
	msg = '~cb: %s.%s' % ( name , cbname )

	if cbname in [ 'autolabel','beforeFrameRender','afterFrameRender','renderProgress', ]:
		return

	if cbname == 'knobChanged':
		k = nuke.thisKnob()
		if k.name() in ['xpos','ypos','selected']:
			return
		msg += '.%s = %s' % ( k.name() , k.value() ) 
		
	sys.__stdout__.flush()
	sys.__stdout__.write( msg + '\n' )


