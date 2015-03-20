

print '\n-> medula/mdl/nuke/menu.py'

'Esto se evalua una sola vez y solo durante la inicializacion del stage MENU'
'No aparecen errores de duplicidad en general'

import nk

nk.startup.consume_menus()

nk.callback.create_callbacks()
