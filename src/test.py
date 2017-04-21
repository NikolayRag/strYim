'''
Yi4k camera required to be available at 192.168.42.1 and telnet-enabled
'''


import kiLog
kiLog.state('YiReader', kiLog.DEBUG)
#kiLog.state('YiPy', kiLog.DEBUG)
kiLog.state('', kiLog.DEBUG)


import logging

import SourceYi4k



yi= SourceYi4k.YiReader()


def yiRes(_res):
	logging.debug('Yi Py res: %s' % _res)

yipy= SourceYi4k.YiPy()
yipy.run('print(2+2)')
yipy.wait(yiRes)


logging.info('End')