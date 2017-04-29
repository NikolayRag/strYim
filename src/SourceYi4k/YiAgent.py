'''
Detect 'loop' file being recorded and continuously read it,
 switching to next in sequence when current is exhaused.

Agent is run at Yi4k side.

Flow:
* loop record
	* detect file being recorded
	* read tail till end
		*? split 264/AAC
		*? make Atoms available to read from socket 
'''
class YiAgent():
	import socket, threading, time, os
	tcpSocket= None



	def __init__(self, _port, _test=None):
		if not self.tcpInit(_port):
			return

		if _test:
			self.test()
		else:
			self.check()



	def tcpInit(self, _port):
		cListen= YiAgent.socket.socket()
		cListen.setsockopt(YiAgent.socket.SOL_SOCKET, YiAgent.socket.SO_REUSEADDR, 1)

		try:
			cListen.bind(('0.0.0.0',_port))
		except Exception as x:
			print('error: %s' % x)
			return

		cListen.listen(1)
		cListen.settimeout(5)

		try:
			c, a= cListen.accept()
		except Exception as x:
			print('error: %s' % x)
			return

		self.tcpSocket= c

		return True



	def send(self, _data):
		try:
			self.tcpSocket.send(_data)
			return True
		except:
			None



	'''
	Close socket.
	If called while running, cause exception in sending data,
	 resulting stop execution.
	'''
	def close(self):
		if not self.tcpSocket:
			return

		self.tcpSocket.close()



	'''
	Normal execution after caller is connected.
	'''
	def check(self):
		fileNew= fileOld= False
		
		#terminated by socket
		while True:
			fileOld= fileNew
			if not self.send('123'):
				return

			YiAgent.time.sleep(.5)

		return



	def xxx(self):
		f= open('/dev/random', 'rb')
		
		block= 100000
		for n in range(10):
			b= f.read(block)
			
			if not self.send(b):
				print('stop')
				return

			if len(b)<block:
				break









	'''
	Test function.
	'''
	def test(self):
		f= open('/dev/random', 'rb')
		
		block= 100000
		while True:
			b= f.read(block)
			
			if not self.send(b):
				print('stop')
				return

			if len(b)<block:
				break
