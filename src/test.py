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
	logging.info('YiPy ok: %s' % yiPyResult[0])
else:
	logging.error('YiPy err')






resCnt= [0]
def agentCB(res):
	resCnt[0]+= len(res or b'')

yi= SourceYi4k.YiReader()
threading.Timer(0, lambda:yi.yiListen(agentCB)).start()

wdog= threading.Timer(6, yi.yiClose)
wdog.start()
yiReaderRes= yi.yiRunAgent('test')
wdog.cancel()


if yiReaderRes:
	logging.info('YiReader ok, total %s bytes' % resCnt[0])
else:
	logging.error('YiReader err')






def metaCB(_res):
	logging.info(_res)

yi= SourceYi4k.YiReader()
threading.Timer(6, yi.yiClose).start()
yiReaderRes= yi.start(metaCB)

logging.info('YiReader: %s' % yiReaderRes)




logging.info('End')
