import logging

import base64, threading, random

from KiTelnet import *


'''
Run Python code at Yi4k side.
Yi4k should have Telnet on (console_enable.script file in SD's root).

Incoming Python code is recieved at Yi side, saved to file and then executed.

Execution is nonblocking.
'''
class YiPy():
	addr= None
	filename= None

	userCB= None
	result= None

	resultBlock= None


	@staticmethod
	def defaults(addr='192.168.42.1', port=1231):
		YiPy.addr= addr
		YiPy.port= port



	'''
	Prepare YiPy object.
	Filename is used to hold Python code being executed,
	 and is random-generated is not specified at YiPy() or .defaults().
	'''
	def __init__(self, addr=None, port=None, filename=None):
		self.filename= filename or ('/tmp/YiPy%s' % str(random.random())[2:])
		self.addr= addr or self.addr
		self.port= port or self.port

		self.resultBlock= threading.Event()
		self.resultBlock.set()	#default nonblocking



	'''
	The function is NOT safe in any sort.

	Send given Python code to Yi and execute it there.
	Function returns immediately.
	Use .wait() for block 'till execution end.

	NC is run using telnet, listening for _content.
	'''
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

		if not self.sendPyCode(_content):
			self.close()
			return

		logging.info('Python code sent')


		return self



	'''
	Block untill code is executed at Yi side.
	If there's no code was started, return.

	If _callback supplied, it will be called instead
	 and function will return instantly.
	'''
	def wait(self, _cb=None):
		if callable(_cb):
			self.userCB= _cb

			return


		self.resultBlock.wait()

		return self.result





	'''
	Private.
	Callback to be called at execution end.
	'''
	def resCB(self, _res):
		self.result= _res

		logging.debug('Result: %s' % _res)


		if callable(self.userCB):
			self.userCB(_res)

		self.close()



	'''
	Private.
	Cleanup function.
	'''
	def close(self):
		telnet= KiTelnet('rm %s' % self.filename, self.addr)
		telnet.result()


		self.resultBlock.set()



	'''
	Private.
	Send Python code for execution to connection opened by NC.
	'''
	def	sendPyCode(self, _content):
		cSock= None

		logging.info('Connecting to nc')
		for n in range(5):
			try:
				cSock= socket.create_connection((self.addr,self.port), 1)
				break
			except:
				None


		if not cSock:
			logging.error('Not connected')
			return

		cSock.send(_content.encode())
		cSock.close()

		return True



YiPy.defaults()
