

import nuke
import mdl
from contextlib import contextmanager

__mod__ = mdl.uber.uberModule()


'Operaciones de render para rendear nodos de cualquier tipo con el frame range marcado'



@contextmanager
def switch_proxy_mode( proxy_mode ):
	
	'classic render function in main thread'
	cur_proxy_mode = nuke.root().proxy()
	nuke.root().setProxy( proxy_mode )
	try:
		yield
	finally:
		nuke.root().setProxy( cur_proxy_mode )


def frame_ranges( nodes ):

	frs = nuke.FrameRanges()
	for n in nodes:
		frs.add( nuke.FrameRange(n.firstFrame(),n.lastFrame(),1) )	

	return frs


def execute_node( node , proxy_mode = False , views = [] ):
#
#	if node.Class() == 'CurveTool':
#
#		node['go'].execute()
#
#	elif node.Class() == 'WriteGeo':
#
#		node['Execute'].execute()
#
#	elif node.Class() == 'Write':
	
	node['reload'].execute()
	views = views or nuke.views()
	frange = node.frameRange()
	
	with switch_proxy_mode( proxy_mode ):
		try:
			print 'rendering views: %s' % str( nuke.views() )
			nuke.execute( node , frange.first() , frange.last() , views , continueOnError = True )
		except RuntimeError,e:
			if e.message.startswith( 'Cancelled;' ):
				print '\nRender of node "%s" %s' % ( node.name(), e.message)
				node['reload'].execute()
			else:
				raise e
	#else:
	#	raise RuntimeError('El nodo "%s" no se puede ejecutar con este comando' % node.name() ) 


def execute_multiple( nodes , proxy_mode = False , views = [] ):

	assert all( [ ( True if n.Class() == 'Write' else False ) for n in nodes ] ), nuke.message( 'No se pueden ejecutar nodos diferentes a Write' )

	for node in nodes: node['reload'].execute()
	views = views or nuke.views()
	ranges = __mod__.frame_ranges( nodes )
	
	with switch_proxy_mode( proxy_mode ):
		nuke.executeMultiple( nodes , ranges , views , continueOnError = True )
	for node in nodes: node['reload'].execute()


def execute_multiple_background( nodes , proxy_mode = False , views = [] ):

	assert all( [ ( True if n.Class() == 'Write' else False ) for n in nodes ] ), nuke.message( 'No se pueden ejecutar nodos diferentes a Write' )
	
	for node in nodes: node['reload'].execute()
	views = views or nuke.views()

	p = nuke.Panel( 'Execute In Background' )
	p.addEnumerationPulldown( 'threads', '1 2 4 8' )
	p.addEnumerationPulldown( 'memory', '512M 1024M 2048M 3072M 4096M' )
	p.show()

	limits = { 'maxThreads' : p.value('threads') , 'maxCache': p.value( 'memory') }

	ranges = __mod__.frame_ranges( nodes )
		
	with switch_proxy_mode( proxy_mode ):	
		print 'rendering views: %s' % str( nuke.views() )
		nuke.executeBackgroundNuke( nuke.EXE_PATH , nodes , ranges , views , limits , continueOnError = True )





