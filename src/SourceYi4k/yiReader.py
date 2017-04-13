import logging

from .yiReaderTelnet import *
from .yiReaderAgent import *


class yiReader():
	telnet= None

	def __init__(self, _ip='192.168.42.1'):
		self.telnet= yiReaderTelnet(_ip)
		
		logging.info('Reader inited')

