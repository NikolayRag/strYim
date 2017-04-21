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
	def defaults(_addr='192.168.42.1', _filename=None):
		YiPy.addr= _addr
		YiPy.filename= _filename

		KiTelnet.defaults(YiPy.addr)



	def __init__(self, filename=None):
		self.filename= filename or self.filename

		self.resultBlock= threading.Event()
		self.resultBlock.set()	#default nonblocking



	def run(self, _content):
		if not self.filename:
			logging.error('No Py file target specified')
			return


		#start over
		self.resultBlock.clear()


		_content= base64.b64encode(_content.encode('ascii')).decode()

		telnet= KiTelnet('echo %s | base64 -d > %s; python %s' % (_content, self.filename, self.filename))
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
