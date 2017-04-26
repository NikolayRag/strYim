import logging, inspect, socket, threading

from .YiPy import *
from .YiAgent import *


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

	def __init__(self, addr='192.168.42.1', port=1231):
		self.yiAddr= addr
		self.yiPort= port
		YiPy.defaults(addr, port+1)
		
		logging.info('Reader inited')



	def yiListen(self):
		self.yiSocket= None

		logging.info('Connecting to nc')
		for n in range(5):
			try:
				self.yiSocket= socket.create_connection((self.yiAddr,self.yiPort), 2)
				break
			except:
				None
			

		if not self.yiSocket:
			logging.error('Not connected')
			return



		logging.info('Yi begin')

		resCnt= 0
		while True:
			try:
				res= self.yiSocket.recv(16384)
			except:
				break

			if res:
				resCnt+= len(res)

		logging.debug('Yi total %s bytes' % resCnt)




	def yiClose(self):
		if self.yiSocket:
			self.yiSocket.close()



	def yiRunAgent(self):
		agentSrc= inspect.getsourcelines(YiAgent)[0]
		agentSrc= ''.join(agentSrc)

		yipy= YiPy()
		if not yipy.run('%s\nYiAgent(%d)' % (agentSrc, self.yiPort)):
			logging.error('Running Yi')
			return True


		res= yipy.wait()

		self.yiClose()


		if res:
			logging.error(res)

		return res
