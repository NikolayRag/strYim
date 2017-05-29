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

	def live(self):
		return self.cFile!=False

	def add(self, _data):
		self.cFile.write(_data)

	def close(self):
		self.cFile.close()




'''
Network sink
'''
import subprocess, threading, socket, os, re
from support import *

class SinkNet(threading.Thread):
	ipMask= re.compile('^((?P<protocol>tcp|udp|rtmp)://)?(?P<addr>(\d+\.\d+\.\d+\.\d+)|([\w\d_\.]+))?(:(?P<port>\d*))?(?P<path>.*)')

# -todo 305 (clean, sink) +0: autodetect free port for ffmpeg
	ffport= 2345
	ffmpeg= None
	ffSocket= None

	protocol= 'flv'
	addr= ''



	def __init__(self, _addr=''):
		self.addr= _addr

		ipElements= self.ipMask.match(_addr)
		ipElements= ipElements and ipElements.group('protocol')
		if ipElements=='udp':
			self.protocol= 'mpegts'


		threading.Thread.__init__(self)
		self.start()

		self.ffSocket= self.tcpInit()



	def live(self):
		if self.ffSocket and self.ffmpeg:
			return True



	def add(self, _data):
		if not self.live():
			return

		try:
			self.ffSocket.sendall(_data)

		except:
			logging.error('Socket error')
			self.ffSocket= None



	def close(self):
		ffSocket= self.ffSocket
		self.ffSocket= None
		if ffSocket:
			ffSocket.close()

		self.ffmpeg and self.ffmpeg.kill()



### PRIVATE

	def run(self):
#  todo 105 (sink, unsure) -1: hardcode RTMP protocol
		logging.info('Running ffmpeg')

		ffmperArg= [ROOT + '/ffmpeg/ffmpeg'] +('-re -i tcp://127.0.0.1:%d?listen -c copy -f' % self.ffport).split()+ [self.protocol, self.addr]
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
		sock= None
		try:
			sock= socket.create_connection(('127.0.0.1',self.ffport), 5)
		except:
			logging.error('Init error')

		return sock

