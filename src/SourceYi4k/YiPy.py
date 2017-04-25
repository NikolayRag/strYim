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


		#recieve Python code over TCP and execute it
		tString= 'nc -l -p 1231 -w 10 > %s; python %s' % (self.filename, self.filename)
		telnet= KiTelnet(tString, self.addr)
		telnet.result(self.resCB)

		self.sendPyCode(_content, 1231)

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

		self.close()



	def close(self):
		self.resultBlock.set()



	'''
	Send Python code for execution to opened by NC connection.
	'''
	def	sendPyCode(self, _content, _port):
		s= socket.socket()
		s.connect((self.addr,_port))
		s.send(_content.encode())
		s.close()



YiPy.defaults()
