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

# =todo 257 (feature, YiAgent) +0: Send agent to camera
# =todo 258 (feature, YiAgent) +0: Run agent at camera
# =todo 259 (feature, YiAgent) +0: Make camera agent


class YiReader():
	yiAddr= None
	yiSocket= None

	def __init__(self, addr='192.168.42.1'):
		self.yiAddr= addr
		YiPy.defaults(addr, '/tmp/agent.py')
		
		logging.info('Reader inited')



	def yiListen(self, _port):
		self.yiSocket= socket.socket()
		try:
			self.yiSocket.connect((self.yiAddr,_port))
		except Exception as x:
			logging.error('Yi connection')
			return

		res= self.yiSocket.recv(16384)

		logging.debug('Yi response: %s' % res.decode())

		return res


	def yiRunAgent(self, _port):
		agentSrc= inspect.getsourcelines(YiAgent)[0]
		agentSrc= ''.join(agentSrc)

		yipy= YiPy()
		yipy.run('%s\nYiAgent(%d)' % (agentSrc, _port))
		res= yipy.wait()

		if res:
			logging.error(res)

		return res
