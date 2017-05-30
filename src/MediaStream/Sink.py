class Sink():
	isLive= True

	dest= ''
	prefix= b''


	'''
	Initialize with destination
	'''
	def __init__(self, _dest, _prefix=b''):
		self.dest= _dest
		self.setPrefix(_prefix)


	'''
	Add binary data to sink
	'''
	def add(self, _data):
		None


	'''
	Close sink. It will not be usable anymore
	'''
	def close(self):
		self.kill()



### PRIVATE, shouldn't be overriden



	'''
	Set binary prefix to store.
	It will be emited at start.
	'''
	def setPrefix(self, _prefix):
		self.prefix= _prefix


	'''
	Check if sink is live
	'''
	def live(self):
		return self.isLive



	'''
	.live() will return false
	'''
	def kill(self):
		self.isLive= False







'''
Mux-suitable sinks
'''
import logging

'''
File sink
'''
class SinkFile(Sink):
	cFile= None



	def __init__(self, _dest, _prefix=b''):
		Sink.__init__(self, _dest, _prefix)

		self.cFile= open(_dest, 'wb')

		self.add(self.prefix)


	
	def add(self, _data):
		if self.live():
			self.cFile.write(_data)



	def close(self):
		self.cFile.close()

		self.kill()






'''
Network sink
'''
import subprocess, threading, socket, os, re
from support import *

class SinkNet(threading.Thread, Sink):
	ipMask= re.compile('^((?P<protocol>tcp|udp|rtmp)://)?(?P<addr>(\d+\.\d+\.\d+\.\d+)|([\w\d_\.]+))?(:(?P<port>\d*))?(?P<path>.*)')

# -todo 305 (clean, sink) +0: autodetect free port for ffmpeg
	ffport= 2345
	ffmpeg= None
	ffSocket= None

	protocol= 'flv'



	def __init__(self, _dest, _prefix=b''):
		Sink.__init__(self, _dest, _prefix)

		ipElements= self.ipMask.match(_dest)
		ipElements= ipElements and ipElements.group('protocol')
		if ipElements=='udp':
			self.protocol= 'mpegts'


		threading.Thread.__init__(self)
		self.start()

		self.ffSocket= self.tcpInit()

		self.add(self.prefix)




	def add(self, _data):
		if not self.live():
			return

		try:
			self.ffSocket.sendall(_data)

		except:
			self.kill()

			logging.error('Socket error')



	def close(self):
		if not self.live():
			return
		self.kill()

		self.ffSocket.close()

		self.ffmpeg.kill()



### PRIVATE

	def run(self):
#  todo 105 (sink, unsure) -1: hardcode RTMP protocol
		logging.info('Running ffmpeg')

		ffmperArg= [ROOT + '/ffmpeg/ffmpeg'] +('-re -i tcp://127.0.0.1:%d?listen -c copy -f' % self.ffport).split()+ [self.protocol, self.dest]
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


		self.kill()

		logging.info('Finished ffmpeg')
		if resultMatch:
			logging.info('speed=%s, %sfps' % (resultMatch.group('speed'), resultMatch.group('fps')))



	def tcpInit(self):
		sock= None
		try:
			sock= socket.create_connection(('127.0.0.1',self.ffport), 5)
		except:
			self.kill()

			logging.error('Init error')

		return sock





import queue
'''
Listen for connections and provide buffered data.
'''
class SinkServer(threading.Thread, Sink):
	socket= None
	dataQ= None



	def __init__(self, _dest='', _prefix=b''):
		Sink.__init__(self, _dest, _prefix)

		self.dataQ= queue.Queue()

		threading.Thread.__init__(self)
		self.start()



	def add(self, _data):
		if not self.live():
			return

		self.dataQ.put(_data)
		if self.dataQ.qsize()>1000: #frames limit
			self.dataQ.get()



	def close(self):
		self.kill()



### SERVER SUPPORT



	def run(self):
		cListen= socket.socket()
		cListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		try:
			cListen.bind(('127.0.0.1',1234))
		except Exception as x:
			print('error: %s' % x)
			return

		cListen.listen(1)
		cListen.settimeout(5)

		while self.live(): #reconnection loop

			try:
				cSocket, a= cListen.accept()
			except Exception as x:
				logging.debug('Listening: %s' % x)

				continue


			cSocket.settimeout(.5)

			cSocket.sendall(self.prefix)


			while self.live():
				try:
					cData= self.dataQ.get(timeout=.1)
				except queue.Empty:
					continue

				try:
					cSocket.sendall(cData)
				except:
					break

			cSocket.close()

		cListen.close()
