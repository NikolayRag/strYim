import logging

import base64, threading

from KiTelnet import *


'''
Run Python code at Yi4k side.
Telnet at Yi4k should be switched on (using console_enable.script in root).


'''
class YiPy():
	addr= None
	filename= None

	userCB= None
	result= None

	resultBlock= None


	@staticmethod
	def defaults(addr='192.168.42.1', port=1231, filename=None):
		YiPy.addr= addr
		YiPy.port= port
		YiPy.filename= filename



	def __init__(self, addr=None, port=None, filename=None):
		self.filename= filename or self.filename
		self.addr= addr or self.addr
		self.port= port or self.port

		self.resultBlock= threading.Event()
		self.resultBlock.set()	#default nonblocking



	def run(self, _content):
		if not self.filename:
			logging.error('No target Python file specified')
			return


		#start over
		self.resultBlock.clear()


		#recieve Python code over TCP and execute it
		tString= 'nc -l -p %d -w 10 > %s; python %s' % (self.port, self.filename, self.filename)
		telnet= KiTelnet(tString, self.addr)
		telnet.result(self.resCB)

		self.sendPyCode(_content)

		logging.info('Python code sent')


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
		telnet= KiTelnet('rm %s' % self.filename, self.addr)
		telnet.result()


		self.resultBlock.set()



	'''
	Send Python code for execution to opened by NC connection.
	'''
	def	sendPyCode(self, _content):
		s= socket.socket()
		s.connect((self.addr,self.port))
		s.send(_content.encode())
		s.close()



YiPy.defaults()
