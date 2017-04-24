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
	import socket, threading
	tcpSocket= None



	def __init__(self, _port):
		if self.tcpInit(_port):
			self.start()

			YiAgent.threading.Timer(2, self.close).start() #temp



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

		self.tcpSocket= c

		return True



	def start(self):
		f= open('/dev/random', 'rb')
		self.tcpSocket.send(f.read(12))



	def close(self):
		self.tcpSocket.close()
