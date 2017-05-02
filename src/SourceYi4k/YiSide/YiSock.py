class YiSock():
	import socket
	global socket

	tcpSocket= None



	def __init__(self, _port):
		self.tcpInit(_port)



	def tcpInit(self, _port):
		cListen= socket.socket()
		cListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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



	def send(self, _binary, _ctx=None):
		dataA= YiData.build(_binary, _ctx)
		try:
			for cData in dataA:
				self.tcpSocket.send(cData)
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



	def valid(self, _test=False):
		if not self.tcpSocket:
			return

		if _test:
			try:
				self.tcpSocket.send(b'')
			except:
				return

		return True
