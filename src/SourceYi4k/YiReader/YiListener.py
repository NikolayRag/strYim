import threading, socket
import logging


'''
Listen to YiAgent in isolated thread.
'''
class YiListener(threading.Thread):
	yiAddr= None
	yiPort= None
	yiSocket= None

	cb= None

	allow= True


	'''
	Connect to YiAgent and listen back.
	start() by demand
	'''
	def __init__(self, _addr, _port, _cb=None):
		threading.Thread.__init__(self)

		self.yiAddr= _addr
		self.yiPort= _port

		self.cb= callable(_cb) and _cb



	def stop(self):
		self.allow= False



### PRIVATE



	def run(self):
		logging.info('Connecting to Agent')
		for n in range(5):
			try:
				self.yiSocket= socket.create_connection((self.yiAddr,self.yiPort), 1)
				break
			except:
				None
			

		if not self.yiSocket:
			logging.error('Not connected')
			return

		self.yiSocket.settimeout(1)


		logging.info('Yi begin')

		while self.allow:
			try:
				res= self.yiSocket.recv(16384)
			except socket.timeout:
				continue
			except Exception as x:
				logging.info('Yi end: %s' % x)
				break

			self.cb and self.cb(res)


		self.yiSocket.shutdown(socket.SHUT_RDWR)
		self.yiSocket.close()

		self.allow= True #prepare for (possible) restart
