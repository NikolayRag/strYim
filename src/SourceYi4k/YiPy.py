import logging

import base64, threading

from KiTelnet import *


'''
'''
class YiPy():
	addr= None
	filename= None

	userCB= None
	result= None

	resultBlock= None


	@staticmethod
	def defaults(addr='192.168.42.1', filename=None):
		YiPy.addr= addr
		YiPy.filename= filename



	def __init__(self, addr=None, filename=None):
		self.filename= filename or self.filename
		self.addr= addr or self.addr

		self.resultBlock= threading.Event()
		self.resultBlock.set()	#default nonblocking



	def run(self, _content):
		if not self.filename:
			logging.error('No Py file target specified')
			return


		#start over
		self.resultBlock.clear()


		_content= base64.b64encode(_content.encode('ascii')).decode()

		telnet= KiTelnet('echo %s | base64 -d > %s; python %s' % (_content, self.filename, self.filename), self.addr)
		telnet.result(self.resCB)

		logging.info('Yi Py sent')


		return self



	def wait(self, _cb=None):
		if callable(_cb):
			self.userCB= _cb

			return


		self.resultBlock.wait()

		return self.result




	def resCB(self, _res):
		self.result= _res

		logging.debug('Result: %s' % _res)


		if callable(self.userCB):
			self.userCB(_res)

		self.resultBlock.set()



YiPy.defaults()
