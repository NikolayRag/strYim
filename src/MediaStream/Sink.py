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
import subprocess, threading, socket, os
from support import *

class SinkRTMP(threading.Thread):
	ffport= 2345
	ffmpeg= None
	rtmp= ''

	cSocket= None


	def __init__(self, _rtmp):
		threading.Thread.__init__(self)

		self.rtmp= _rtmp

		self.start()

		self.cSocket= self.tcpInit()





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

		self.ffmpeg.kill()



### PRIVATE

	def run(self):
#  todo 105 (sink, unsure) -1: hardcode RTMP protocol
		logging.info('Running ffmpeg')

		ffmperArg= [ROOT + '/ffmpeg/ffmpeg', '-i', 'tcp://127.0.0.1:%d?listen' % self.ffport, '-c', 'copy', '-f', 'flv', self.rtmp]
		if sys.platform.startswith('win'):
			self.ffmpeg= subprocess.Popen(ffmperArg, stderr=subprocess.PIPE, stdin=subprocess.PIPE, bufsize=1, universal_newlines=True, creationflags=0x00000200)
		else:
			self.ffmpeg= subprocess.Popen(ffmperArg, stderr=subprocess.PIPE, stdin=subprocess.PIPE, bufsize=1, universal_newlines=True, preexec_fn=os.setpgrp)


		resultMatch= None
		while not self.ffmpeg.poll():
			ffResult= self.ffmpeg.stderr.readline()

			resultMatch= re.match('.*Unknown error occurred.*', ffResult)
			if resultMatch:
				logging.error('FFmpeg')

			resultMatch= re.match('frame=\s+(?P<frames>[\d]+)\s+fps=\s+(?P<fps>[\d\.]+)\s+q=(?P<q>-?[\d\.]+)\s+size=\s+(?P<size>[\d]+[kmg]?B)\s+time=(?P<time>[\d\:\.]+)\sbitrate=(?P<bitrate>[\d\.]+k?bits/s)\sspeed=(?P<speed>[\d\.]+x)', ffResult)
			if resultMatch:
				logging.debug('speed=%s, %sfps' % (resultMatch.group('speed'), resultMatch.group('fps')))


		self.ffmpeg= None

		logging.info('Finished ffmpeg')
		if resultMatch:
			logging.info('speed=%s, %sfps' % (resultMatch.group('speed'), resultMatch.group('fps')))


	def tcpInit(self):
		return socket.create_connection(('127.0.0.1',self.ffport))

