'''
Agent is run at Yi4k side.

Agent flow:
* loop record
	* detect file being recorded
	* read tail till end
		*? split 264/AAC
		*? make Atoms available to read from socket 
'''
class YiAgent():
	import socket, threading
	tcpSocket= None



	def __init__(self, _port, _test=None):
		if not self.tcpInit(_port):
			return

		if _test:
			self.test()
		else:
			self.start()

		self.close()




	def tcpInit(self, _port):
		cListen= YiAgent.socket.socket()
		cListen.setsockopt(YiAgent.socket.SOL_SOCKET, YiAgent.socket.SO_REUSEADDR, 1)

		try:
			cListen.bind(('0.0.0.0',_port))
		except Exception as x:
			print('error: %s' % x)
			return

		cListen.listen(1)

		try:
			c, a= cListen.accept()
		except Exception as x:
			print('error: %s' % x)
			return

		self.tcpSocket= c

		return True



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



	def send(self, _data):
		try:
			self.tcpSocket.send(_data)
			return True
		except:
			None



	def close(self):
		if not self.tcpSocket:
			return

		self.tcpSocket.close()
