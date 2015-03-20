

import nuke
import mdl
import threading
import time


def __call__( self , *args , **kwargs ):
	#__mod__.__mod__
	return __mod__.taskbar( *args , **kwargs )

__mod__ = mdl.uber.uberModule()


'taskbar debe ser un consumer, es decir recibe una funcion a la que llama\
de forma regular, ejecutando la tarea y recibiendo una serie de datos que\
determinan el estatus del taskbar. Cuando se consume el proceso o hay un\
error en la tarea se sale y se borra el tb'

#generator








def taskbar( generator , label = None , send_status = False , lag = 0 ):

	vars().update( locals() )

	label = label or generator.__name__

	'generic taskbar'

	#label , generator = label , generator

	def taskbar_thread():

		tb = nuke.ProgressTask( label )
		gen = generator()
		
		while 1:
		
			try:

				msg_and_percent = gen.next()
				
				if msg_and_percent == None:
					gen.close()
					break

				msg,percent = msg_and_percent
				tb.setMessage( msg )
				tb.setProgress( percent )
				

				isCancelled =  tb.isCancelled()

				if send_status:
					gen.send( 1 if isCancelled else 0 )
					
					'El generador es el encargado de cerrar el taskbar'

				else:
					if isCancelled:
						gen.close()
						break

			except StopIteration:
				break
			except:
				print mdl.uber.format_exception()
				break
			
			time.sleep( lag )

			#print mdl.uber.debug()

		del tb
			

	thr = threading.Thread( None , taskbar_thread )
	thr.daemon = True
	thr.start()
	return  thr



def test():

	def gen():

		total = 50

		for i in range(total):

			msg = 'item no %s' % i 
			per = i*100/total
	
			'una vez que ha hecho parte de la tarea suelte el item'
			yield msg,per

			'do work here'
			print 'Doing Long Task',i
			time.sleep(.1)
			print 'Done Task',i

			#print  mdl.uber.debug()

			isCancelled = yield
			if isCancelled: 
				'si el taskbar se cancela'
				return


	return __mod__.taskbar( 'test' , gen , send_status = True )






#
#
#				'No hay conexion'
#				if not REMOTE.alive(): 
#					print 'Sin conexion'
#					return
#				
#				proxy = REMOTE.proxy
#
#				'Un error que da en windows, debe ser por los threads'
#				if not proxy: continue
#
#				if tb.isCancelled():
#					proxy.cancel( key )
#					return
#
#				info = proxy.info( key )
#
#				'termina el taskbar'
#				if info == None: 
#					print 'Tarea terminada : ' , key
#					return