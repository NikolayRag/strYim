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
	tcpSockOne= None



	def __init__(self, _port):
		if self.tcpInit(_port):
			self.start()



	def tcpInit(self, _port):
		cListen= YiAgent.socket.socket()
		cListen.setsockopt(YiAgent.socket.SOL_SOCKET, YiAgent.socket.SO_REUSEADDR, 1)

		try:
			cListen.bind(('0.0.0.0',_port))
		except Exception as x:
			print(x)
			return

		cListen.listen(1)

		try:
			c, a= cListen.accept()
		except Exception as x:
			print(x)
			return

		self.tcpSockOne= c

		return True


	def start(self):
		f= open('/dev/random', 'rb')
		self.tcpSockOne.send(f.read(12))
