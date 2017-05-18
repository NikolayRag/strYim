import logging
logging.basicConfig(level= logging.DEBUG)


from KiTelnet import *


def tr(res):
	logging.info('T CB: %s' % res.decode())


KiTelnet.defaults('192.168.42.1')
logging.info('T defaults')

telnet= KiTelnet('echo x')
logging.info('T init')

result= telnet.result(tr)
logging.info('T result()')
