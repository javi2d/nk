
import sys
import nuke
import fnmatch

from contextlib import contextmanager

import mdl

'Solvers de comandos'
CMD_SOLVERS = {}

'Listado de roots de carga de comandos, para recarga'
CMD_SRC_ROOTS = []

'Listado de comandos cargados (consumible)'
CMD_COMMANDS = []
'Listado de viewerPorcesses cargados (consumible)'
CMD_VPROCESS = []

PARAMS_FILE = 'params.dspace.py'   


FOLDER_PARAMS = [ ('name',''),('icon',None),('index',-1)]

FILE_PARAMS = FOLDER_PARAMS + [ ('tooltip',''),('shortcut','') ]

'addCommand(self, name, command, shortcut, icon, tooltip, index, readonly)'
def __call__( self , *args , **kwargs ):
	return __mod__.command( *args , **kwargs )

__mod__ = mdl.uber.uberModule()

'quick_cmd : decorador para convertir una funcion en un comando de forma rapida'



'addCommand(self, name, command, shortcut, icon, tooltip, index, readonly)'
def command( route , *args , **kwargs ):
	#print 1.1,route
	'Crea un comando decorando una funcion'
	def create_command( func ):
		#print 1,func
		assert nuke.GUI, '~ unable to create command %s, not in nuke.GUI mode.' % func
		menu,name  = route.partition('/')[::2]
		menu = nuke.toolbar( menu )
		menu.addCommand( name , func , *args , **kwargs )
		return func
	
	return create_command




def reload_commands():
	
	roots = __mod__.CMD_SRC_ROOTS[:]
	for root in roots:
		print 'reloading commands of root: "%s"' % root
		__mod__.load_commands( root )
	
	__mod__.flush_commands()



def load_commands( root ):
	
	# Carga los comandos que encuentre bajo root
	# 
	'Carga los comandos bajo root'
	'Simplemente almacena los comando y los vps en listas '

	root = mdl.shell( root , delegated = True ).MAKE
	assert root.ISDIR

	if root in __mod__.CMD_SRC_ROOTS: 
		__mod__.CMD_SRC_ROOTS.remove( root )
	__mod__.CMD_SRC_ROOTS.append( root )

	include = lambda i: not i.startswith('__') and not i.startswith('.')
	
	'part 1, recopilacion de comandos'
	for P,D,F in root.WALK:
		
		if fnmatch.filter( F , '*.gizmo' ):
			nuke.pluginAddPath( P , addToSysPath=False )

		if P == root:
			D[:] = filter( include , D )

		elif P.endswith( '/ViewerProcess' ) and P.PARENT == root:
			D[:] = []
			for f in filter( include , F ):
				fsh = P(f)
				if fsh.TAGEXT in [ '.gizmo','.3dl','.blut','.cms','.csp','.cub','.cube','.vf','.vfz']:	
					__mod__.CMD_VPROCESS.append( fsh )
		else:

			D[:] = filter( include , D )
			for f in filter( include , F ):
				fsh = P(f).PY_SOURCE
				if fsh.TAGEXT in __mod__.CMD_SOLVERS:
					__mod__.CMD_COMMANDS.append( (root,fsh) )

					#print 'fooound cms' , fsh

					#relpath = fsh.TAGROOT.relpath( root )
					#if relpath not in dict( __mod__.CMD_COMMANDS ):
					#	__mod__.CMD_COMMANDS.append( (relpath,fsh) )







def createViewerProcessNode( path ):

	path = mdl.shell( path )

	if path.EXT == '.gizmo':
		return nuke.createNode( path.BASENAME )
	else:
		n = nuke.createNode( "Vectorfield" )
		n.knobs()['vfield_file'].setValue( path )

		#Names = ['interpolation', 'gpuExtrapolate', 'colorspaceIn', 'colorspaceOut']
		#for Value in ['trilinear field' , True , 'linear' , 'linear']:
		#	name = Names.pop(0)
		#	n.knobs()[ name ].setValue( Value )

		return n	


def __fix():

	import fbp

	old = mdl.data.DataSpace( fbp.sh( 'cmds/args.cfg' ) )
	new = mdl.data.DataSpace( fbp.sh( 'cmds' )( __mod__.PARAMS_FILE ) )
	
	for k,v in new.iteritems():
		if k in old:
			new[k] = old[k]

	new.dump()


	  



'flush commands'
def flush_commands():

	'Crea en el interfaz los menus y comandos'
	while __mod__.CMD_VPROCESS:
		
		path = __mod__.CMD_VPROCESS.pop(0)
		nuke.ViewerProcess.register( path.NAME , __mod__.createViewerProcessNode , ( path , ) )		
		
		sys.__stdout__.flush()
		sys.__stdout__.write( '+vprocess -> %s\n' % path.BASENAME  )

	roots = []

	'ultimo item falso para terminar los params'

	while __mod__.CMD_COMMANDS:

		root , path = __mod__.CMD_COMMANDS.pop(0)
		'root es usado como limite para las busquedas'

		if root not in roots:
			params = mdl.data.DataSpace( root( __mod__.PARAMS_FILE ) )
			roots.append( root )

		__mod__.create_command( root , path , params )

		if params.mem_changed(): params.dump()


	
'usada internamente por flush commands'
def create_command( root , cmd_path , params ): #= None 

	'Crea un comando con la rute y el fichero'

	root  = mdl.shell( root )
	cmd_path = mdl.shell( cmd_path )
	
	route = cmd_path.relpath( root )
	
	chunks = route.split('/')

	menu = None
	path = root
	
	while chunks:
		
		'Mientras haya elementos en el subpath'
		item = chunks.pop(0)
		path = path( item )

		'Si el menu inicial no ha sido definido lo hacemos'
		if menu == None:
			'esto tiene que ir aqui pq si no los commandos en el raiz no funcionan'
			root_menu = menu = nuke.menu( item )
			continue

		if chunks: 
			args = dict( __mod__.FOLDER_PARAMS )
			#if params != None:
			args = params.setdefault( path.relpath( root ) ,  args )

		else:
			args = dict( __mod__.FILE_PARAMS )
			#if params != None:
			args = params.setdefault( path.TAGNAME ,  args )
		
		'copia'
		args = dict( args )

		'Creacion de menu o comando'

		args['name'] = args.get('name') or item
		args['icon'] = args.get('icon') or __mod__.find_icon( root , path ) 

		if chunks:
			'carga args del menu, los menus no se recargan'
			menu = menu.addMenu( **args )
		else:
			'alcanzamos el archivo '
			'Dos tipos de invocacion, la funcional no funciona al menos en Animation'
			if root_menu.name() in 'Animation'.split():
				default_cmd =  "nk.cmd.invoke('%s')" % path
			else:
				'Esta es necesaria para que aparezcan bien los tracebacks, en la otra lo hace mal'
				default_cmd =  __mod__.launch_command( path )

			args['command'] = args.get('command') or default_cmd
			
			args['icon'] = args['icon'] or 'Modify.png'
			cmd = menu.addCommand( **args )

			sys.__stdout__.flush()
			sys.__stdout__.write( '+cmd %s [ %s ]\n' % ( path.relpath( root ) , cmd.name()   ) )
	

		



def launch_command( path ):
	def cmd():
		__mod__.invoke( path )
	return cmd





def find_icon( root , path  ):
	'sh es el punto de comienzo, root es el limite'
	path = mdl.shell( path )
	root = mdl.shell( root )

	assert path.startswith( root + '/' )
	
	while 1:
		if path == root:
			return None
		icon_path = path( '__init__.png' ) if path.ISDIR else mdl.shell( path.TAGROOT + '.png' )
		if icon_path.EXISTS: 
			return icon_path
		path = path.DIRNAME




def invoke( path ):
	
	fsh = mdl.shell( path , delegated = True ).PY_SOURCE
	solver = __mod__.CMD_SOLVERS[ fsh.TAGEXT ]
	print '~ nk.cmd.invoke [%s] ->' % fsh.BASENAME
	solver( fsh )



def solver( *exts ):
	def deco( solver ):
		for ext in exts: 
			__mod__.CMD_SOLVERS[ext] = solver
	return deco



@solver( '.py' , '.pyc' , '.pyo', '.marshal' )
def python_solver( fsh ):
	'Evaluacion incondicional'
	fsh.EVAL

@solver( '.gizmo'  )
def gizmo_solver( fsh ):
	nuke.createNode( fsh.TAGNAME )

@solver( '.nk'  )
def nuke_solver( fsh ):
	try:
		group = nuke.createNode('Group')
		nodes = []
		group.run( lambda : nuke.scriptReadFile( fsh )  )
	except:
		raise		
	finally:
		nodes = group.nodes()
		group.expand()	
		( n.setSelected( True ) for n in nodes )





