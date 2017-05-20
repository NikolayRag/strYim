'''
Socket used in YiAgent.
The main thing it used for, is wrapping binary data chunks with headers
 to restore chunks back later.

Init with accepting one connection to send data into.
'''
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
# -todo 301 (YiAgent, fix, network) +2: settimg timeout breaks entire transfer
#		self.tcpSocket.settimeout(1)

		return True



	'''
	Prefix esnt data with header.
	'''
	def send(self, _binary=b'', _ctx=0):
		header= YiData.message(YiData.DATA, [_ctx, _binary])
		try:
			self.tcpSocket.send(header)
			self.tcpSocket.send(_binary or b'')
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

		self.msgStop()
		
		self.tcpSocket.shutdown(socket.SHUT_RDWR)
		self.tcpSocket.close()



	'''
	Check if socket is not dropped at other side, sending dummy message into it.
	'''
	def valid(self):
		if not self.tcpSocket:
			return

		dummy= YiData.message()
		try:
			self.tcpSocket.send(dummy)
		except:
			return

		return True



	def msgOverflow(self, _len):
		header= YiData.message(YiData.OVERFLOW, _len)
		try:
			self.tcpSocket.send(header)
			return True
		except:
			None


	def msgStop(self):
		header= YiData.message(YiData.STOP)
		try:
			self.tcpSocket.send(header)
			return True
		except:
			None

	def msgLog(self, _data):
		for i in range(0, len(_data), 15):
			header= YiData.message(YiData.LOG, _data[i:i+15] )
			try:
				self.tcpSocket.send(header)
			except:
				return None

		return True
