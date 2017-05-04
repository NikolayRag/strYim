import logging

import base64, threading, random

from KiTelnet import *


'''
Run Python code at Yi4k side.
Yi4k should have Telnet on (console_enable.script file in SD's root).

Incoming Python code is recieved at Yi side by netcat,
 saved to file and then executed. Result of execution is then returned.

Execution is nonblocking.

WARNING: Switching telnet on and leaving default WIFI password
makes camera vulnerable.
Aside from unsafety of running arbitrary Python code itself with camera.
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
	 and is random-generated if not specified explicitly.
	File is deleted after execution, if YiPy proccess terminated normally.
	'''
	def __init__(self, addr=None, port=None, filename=None):
		self.filename= filename or ('/tmp/YiPy%s' % str(random.random())[2:])
		self.addr= addr or self.addr
		self.port= port or self.port

		self.resultBlock= threading.Event()
		self.resultBlock.set()	#default nonblocking



	'''
	Send given Python code to Yi and execute it there.
	Function returns immediately.
	Use .wait() for block till execution end.
	'''
	def run(self, _content):
		if not self.filename:
			logging.error('No target Python file specified')
			return


		#start over
		self.resultBlock.clear()


		#recieve Python code over TCP and execute it
		tString= 'nc -l -p %d -w 10 > %s; python %s; rm -f %s' % (self.port, self.filename, self.filename, self.filename)
		telnet= KiTelnet(tString, self.addr)
		telnet.result(self.resCB)

		if not self.sendPyCode(_content):
			self.close()
			return

		logging.info('Python code sent')


		return self



	'''
	Block untill code is executed at Yi side.
	Return if there's no code was started.

	If callback supplied, it will be called in time, provided with result.
	 Function will return instantly.
	'''
	def wait(self, _cb=None):
		if callable(_cb):
			self.userCB= _cb

			if self.resultBlock.is_set(): #somehow finished, maybe by error
				self.userCB(None)

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
		self.resultBlock.set()



	'''
	Private.
	Send Python code for execution to connection opened by netcat.
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
