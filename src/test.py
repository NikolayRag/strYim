'''
Yi4k camera required to be available at 192.168.42.1 and telnet-enabled
'''


import kiLog
kiLog.state('YiReader', kiLog.DEBUG)
kiLog.state('YiPy', kiLog.DEBUG)
kiLog.state('', kiLog.INFO)


import logging, threading

import SourceYi4k



yipyBlock= threading.Event()
yiPyResult= [None]
def yiRes(_res):
	yiPyResult[0]= _res
	logging.debug('Yi Py res: %s' % _res)
	yipyBlock.set()

yipy= SourceYi4k.YiPy()
yipy.run('print(2+2)')

logging.debug('YiPy wait')
yipy.wait(yiRes)
yipyBlock.wait()

if yiPyResult[0]==b'4\r\n':
	logging.info('YiPy ok')
else:
	logging.error('YiPy err')



yi= SourceYi4k.YiReader()
threading.Timer(0, yi.yiListen).start()
threading.Timer(5, yi.yiClose).start()
yiRes= yi.yiRunAgent('test')

if not yiRes:
	logging.info('YiReader ok')
else:
	logging.error('YiReader err')



logging.info('End')
