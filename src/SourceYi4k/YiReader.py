import logging, inspect, socket, threading

from .YiPy import *
from .YiSide import *


'''
YiReader controls camera to provide h264+aac byte stream.

YiReader flow:

* send agent to camera
* run agent at camera side
* connect to agent
	* recieve Atom data
		* decode AAC

'''

#  todo 260 (YiAgent, check) +0: catch recording stops or cannot start
#  todo 261 (YiAgent, check) +0: set camera settings


class YiReader():
	yiAddr= None
	yiSocket= None

	runFlag= False


	def __init__(self, addr='192.168.42.1', port=1231):
		self.yiAddr= addr
		self.yiPort= port
		
		logging.info('Reader inited')



	def start(self, _metaCB=None, _dataCB=None):
		if self.yiSocket:
			logging.warning('Already running')

			return False


		yiData= YiData(_metaCB, _dataCB)

		threading.Timer(0, lambda:self.yiListen(yiData.restore)).start()
		
		return self.yiRunAgent()



	def yiClose(self):
		if not self.yiSocket:
			return
		
		logging.info('Close')

		self.runFlag= False



#PRIVATE



	def yiListen(self, _cb=None):
		self.runFlag= True
		self.yiSocket= None

		logging.info('Connecting to nc')
		for n in range(5):
			try:
				self.yiSocket= socket.create_connection((self.yiAddr,self.yiPort), 1)
				break
			except:
				None
			

		if not self.yiSocket:
			logging.error('Not connected')
			return



		logging.info('Yi begin')

		while self.runFlag:
			try:
				res= self.yiSocket.recv(16384)
				callable(_cb) and _cb(res)
			except socket.timeout:
				pass
			except Exception as x:
				logging.info('Yi end: %s' % x)
				break

		self.yiSocket.close()
		self.yiSocket= None



	def yiRunAgent(self, _agentParam=''):
		agentSrc= []
		agentSrc.extend( inspect.getsourcelines(YiData)[0] )
		agentSrc.extend( inspect.getsourcelines(YiSock)[0] )
		agentSrc.extend( inspect.getsourcelines(YiAgent)[0] )
		agentSrc= ''.join(agentSrc)

		yipy= YiPy(self.yiAddr, self.yiPort+1) #Use different ports for YiPy and YiAgent to avoid interferention
		if not yipy.run('%s\nYiAgent(%d,"%s")' % (agentSrc, self.yiPort, _agentParam)):
			logging.error('Running Yi')
			return True


		res= yipy.wait()


		if res:
			logging.error(res)

		return not res

