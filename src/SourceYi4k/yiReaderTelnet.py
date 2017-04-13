import logging


class yiReaderTelnet():
	ip= None

	def __init__(self, _ip):
		self.ip= _ip
		
		logging.info('Telnet inited')
		