'''
Mux-suitable sinks
'''
import logging

'''
File sink
'''
class SinkFile():
	cFile= None

	def __init__(self, _fn):
		self.cFile= open(_fn, 'wb')

	def add(self, _data):
		self.cFile.write(_data)

	def close(self):
		self.cFile.close()





import re, threading
'''
TCP sink
'''
class SinkTCP():
	ipMask= re.compile('^(tcp://)?(?P<addr>(\d+\.\d+\.\d+\.\d+)|([\w\d_\.]+))?(:(?P<port>\d*))?$')

	cSocket= None

	def __init__(self, _ip=''):
		ipElements= self.ipMask.match(_ip)
		addr= ipElements.group('addr') or '127.0.0.1'
		port= int(ipElements.group('port') or 2345)

		self.cSocket= socket.create_connection((addr,port))

		logging.info('Connected to %s, %d' % (addr,port))


	def add(self, _data):
		if not self.cSocket:
			return

		try:
			self.cSocket.sendall(_data)

		except:
			logging.error('Socket error')
			self.cSocket= None



	def close(self):
		cSocket= self.cSocket
		self.cSocket= None
		if cSocket:
			cSocket.close()



### PRIVATE

	def send(self, _data):
		try:
			self.cSocket.sendall(_data)

		except:
			logging.error('Socket error')






'''
RTMP sink
'''
import subprocess, threading, socket
from support import *

class SinkRTMP():
	rtmp= ''

	cSocket= None


	def __init__(self, _rtmp):
		self.rtmp= _rtmp


		ffport= 2345
		threading.Timer(0, lambda: self.serverInit(ffport)).start()
		self.cSocket= self.tcpInit(ffport)





	def add(self, _data):
		if not self.cSocket:
			return

		try:
			self.cSocket.sendall(_data)

		except:
			logging.error('Socket error')
			self.cSocket= None



	def close(self):
		cSocket= self.cSocket
		self.cSocket= None
		if cSocket:
			cSocket.close()




### PRIVATE

	def serverInit(self, _ffport):
#  todo 105 (sink, unsure) -1: hardcode RTMP protocol
		logging.info('Running ffmpeg')

		ffmperArg= [ROOT + '/ffmpeg/ffmpeg', '-i', 'tcp://127.0.0.1:%d?listen' % _ffport, '-c', 'copy', '-f', 'flv', self.rtmp]
		ffmpeg= subprocess.Popen(ffmperArg, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True, preexec_fn=os.setpgrp)

		while not ffmpeg.poll():
			ffResult= ffmpeg.stderr.readline()

			resultMatch= re.match('.*Unknown error occurred.*', ffResult)
			if resultMatch:
				logging.error('FFmpeg')

			resultMatch= re.match('frame=\s+(?P<frames>[\d]+)\s+fps=\s+(?P<fps>[\d\.]+)\s+q=(?P<q>-?[\d\.]+)\s+size=\s+(?P<size>[\d]+[kmg]?B)\s+time=(?P<time>[\d\:\.]+)\sbitrate=(?P<bitrate>[\d\.]+k?bits/s)\sspeed=(?P<speed>[\d\.]+x)', ffResult)
			if resultMatch:
				logging.debug('speed=%s, %sfps' % (resultMatch.group('speed'), resultMatch.group('fps')))



	def tcpInit(self, _ffport):
		return socket.create_connection(('127.0.0.1',_ffport))

