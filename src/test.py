'''
Yi4k camera required to be available at 192.168.42.1 and telnet-enabled
'''


import kiLog
kiLog.state('YiReader', kiLog.DEBUG)
#kiLog.state('YiPy', kiLog.DEBUG)
kiLog.state('', kiLog.INFO)


import logging, threading

import SourceYi4k



yipyBlock= threading.Event()
def yiRes(_res):
	logging.debug('Yi Py res: %s' % _res)
	yipyBlock.set()

yipy= SourceYi4k.YiPy()
yipy.run('print(2+2)')

logging.debug('YiPy wait')
yipy.wait(yiRes)
yipyBlock.wait()

logging.info('YiPy ok')



yi= SourceYi4k.YiReader()
threading.Timer(0, lambda:yi.yiListen()).start()
yiRes= yi.yiRunAgent()
if not yiRes:
	logging.info('YiReader ok')
else:
	logging.error('YiReader err')



logging.info('End')