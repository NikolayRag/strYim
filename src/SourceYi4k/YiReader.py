import logging

from .YiPy import *
from .YiReaderAgent import *


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
	telnet= None

	def __init__(self, addr='192.168.42.1'):
		YiPy.defaults(addr, '/tmp/agent.py')
		
		logging.info('Reader inited')





	def test(self):
		self.telnet= KiTelnet('cat /tmp/wifi.conf')
		logging.info('test telnet in')
		logging.debug(len(self.telnet.result().decode()))
		logging.info('test telnet out')

		