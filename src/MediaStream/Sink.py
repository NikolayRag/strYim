import logging
from .Mux import *


class Sink():
	isLive= True

	dest= ''
	muxer= None



	'''
	Initialize with destination
	'''
	def __init__(self, _dest, _muxer):
		self.dest= _dest
		if isinstance(_muxer, Mux):
			self.muxer= _muxer
		else:
			logging.warning('Muxer is not specified or invalid, bypass')

			self.muxer= Mux()



	'''
	Mux atom into sink
	'''
	def add(self, _atom):
		if self.live():
			return True



	'''
	Close sink. It will not be usable anymore
	'''
	def close(self):
		self.kill()



### PRIVATE, shouldn't be overriden



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



	def __init__(self, _dest, _muxer=None):
		Sink.__init__(self, _dest, _muxer)

		self.cFile= open(_dest, 'wb')

		self.write(self.muxer.header())


	
	def add(self, _atom):
		if self.live():
			return self.write(self.muxer.add(_atom))



	def close(self):
		self.write(self.muxer.finish())

		self.cFile.close()

		self.kill()



### PRIVATE



	def write(self, _data):
		if _data:
			self.cFile.write(_data)

		return True





'''
Network sink
'''
import subprocess, threading, socket, os, re
from support import *

class SinkNet(threading.Thread, Sink):
	ipMask= re.compile('^((?P<protocol>\w+)://)?(?P<addr>(\d+\.\d+\.\d+\.\d+)|([\w\d_\.]+))?(:(?P<port>\d*))?(?P<path>.*)')

# -todo 305 (clean, sink) +0: autodetect free port for ffmpeg
	ffport= 2345
	ffmpeg= None
	ffSocket= None

	protocol= 'flv'



	def __init__(self, _dest, _muxer=None):
		Sink.__init__(self, _dest, _muxer)

		ipElements= self.ipMask.match(_dest)
		ipElements= ipElements and ipElements.group('protocol')
		if ipElements=='udp':
			self.protocol= 'mpegts'


		threading.Thread.__init__(self)
		self.start()

		self.ffSocket= self.tcpInit()

		self.write(self.muxer.header())




	def add(self, _atom):
		if self.live():
			return self.write(self.muxer.add(_atom))



	def close(self):
		self.write(self.muxer.finish())

		if not self.live():
			return
		self.kill()

		self.ffSocket.close()

		self.ffmpeg.kill()



### PRIVATE



	def write(self, _data):
		try:
			if _data:
				self.ffSocket.sendall(_data)

			return True

		except:
			self.kill()

			logging.error('Socket error')



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
	ipMask= re.compile('^((?P<protocol>\w+)://)?(?P<addr>(\d+\.\d+\.\d+\.\d+)|([\w\d_\.]+))?(:(?P<port>\d*))?(?P<path>.*)')

	addr= '127.0.0.1'
	port= 1234

	socket= None
	dataQ= None
# -todo 323 (args, sink) +0: add TCP buffer size arg
	limitIdle= (250, 250) #limit, drop to: without connection
	limitCycle= (500, 250) #limit, drop to: with connection
	limit= None #current


	def __init__(self, _dest='', _muxer=None):
		ipElements= self.ipMask.match(_dest)
		if ipElements:
			self.addr= ipElements.group('addr')
			self.port= int(ipElements.group('port'))


		Sink.__init__(self, _dest, _muxer)

		self.dataQ= queue.Queue()
		self.limit= self.limitIdle

		threading.Thread.__init__(self)
		self.start()



	def add(self, _atom):
		if self.live():
			data= self.muxer.add(_atom)
			if data:
				self.dataQ.put(data)

				if self.dataQ.qsize()>self.limit[0]: #frames trigger
					if self.limit == self.limitCycle:
						logging.error('Buffer full')

					while self.dataQ.qsize()>self.limit[1]: #drop
						self.dataQ.get()

				logging.debug('Buffered in: %d' % self.dataQ.qsize())
			return True



	def close(self):
		self.kill()



### SERVER SUPPORT



	def run(self):
		cListen= socket.socket()
		cListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		try:
			cListen.bind((self.addr,self.port))
		except Exception as x:
			logging.error('Connection: %s' % x)
			return

		cListen.listen(1)
		cListen.settimeout(5)

		while self.live(): #reconnection loop

			try:
				cSocket, a= cListen.accept()
			except Exception as x:
				logging.debug('Listening: %s' % x)

				continue

			logging.info('connected')


			cSocket.settimeout(5)
			cHeader= self.muxer.header() or b''
			try:
				cSocket.sendall(cHeader)
			except:
				self.kill()


			self.limit= self.limitCycle

			while self.live():
				try:
					cData= self.dataQ.get(timeout=.1)
				except queue.Empty:
					continue

				try:
					cSocket.sendall(cData or b'')
				except Exception as x:
					logging.info('Socket error: %s' % x)
					break


			try:
				cSocket.sendall(self.muxer.finish() or b'')
			except:
				pass


			cSocket.close()

			self.limit= self.limitIdle


		cListen.close()
