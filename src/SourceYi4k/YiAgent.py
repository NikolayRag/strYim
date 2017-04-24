'''
Agent is run at Yi4k side.

Agent flow:
* loop record
	* detect file being recorded
	* read tail till end
		* split 264/AAC
		* make Atoms available to read from socket 
'''
class YiAgent():
	import socket
	tcpSockListen= None
	tcpSockOne= None



	def __init__(self, _port):
		if self.tcpInit(_port):
			self.tcpSockOne.send(b'12ddd34')



	def tcpInit(self, _port):
		self.tcpSockListen= YiAgent.socket.socket()

		try:
			self.tcpSockListen.bind(('192.168.42.1',_port))
		except Exception as x:
			print(x)
			return

		self.tcpSockListen.listen(1)

		try:
			c, a= self.tcpSockListen.accept()
		except Exception as x:
			print(x)
			return

		self.tcpSockOne= c

		return True
