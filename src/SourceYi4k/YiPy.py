import logging

import base64

from KiTelnet import *


'''
'''
class YiPy():
	addr= None
	filename= None

	userCB= None
	result= None


	@staticmethod
	def defaults(_addr='192.168.42.1', _filename='/tmp/agent.py'):
		YiPy.addr= _addr
		YiPy.filename= _filename

		KiTelnet.defaults(YiPy.addr)



	def __init__(self, filename=None):
		self.filename= filename or self.filename



	def run(self, _content, _cb=None):
		if not self.filename:
			logging.error('No Py file target specified')
			return


		self.userCB= _cb

		_content= base64.b64encode(_content.encode('ascii')).decode()

		telnet= KiTelnet('echo %s | base64 -d > %s; python %s' % (_content, self.filename, self.filename))
		telnet.result(self.resCB)

		logging.info('Yi Py sent')



	def resCB(self, _res):
		self.result= _res

		logging.debug('Result: %s' % _res)


		if callable(self.userCB):
			self.userCB(_res)



YiPy.defaults()
