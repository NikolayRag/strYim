'''
Continuously read loop-recorded files as soon as record is on.
Reading is started every time loop recording is detected.

Agent is run at Yi4k side.

Flow:
* continouosly detect file being recorded
* read tail
	* till next file in queue is recorded
		* repeat read
'''
class YiAgent():
	import socket, threading, time, os, glob, re


	camRoot= '/tmp/fuse_d/DCIM'
	camMask= '???MEDIA/L???????.MP4'
	camMaskRe= re.compile('^.*(?P<dir>\d\d\d)MEDIA/L(?P<seq>\d\d\d)(?P<num>\d\d\d\d).MP4$')

	liveOldAge= 4 #maximum number of seconds to consider tested file 'live'
	liveTriggerSize= 1000000 #minimum file size to start reading
	livePrefetch= 1500000 #file shorter than this will be started from 0

	tcpSocket= None



	def __init__(self, _port, _test=None):
		if not self.tcpInit(_port):
			return

		if _test:
			self.test()
		else:
			self.check()



	def tcpInit(self, _port):
		cListen= YiAgent.socket.socket()
		cListen.setsockopt(YiAgent.socket.SOL_SOCKET, YiAgent.socket.SO_REUSEADDR, 1)

		try:
			cListen.bind(('0.0.0.0',_port))
		except Exception as x:
			print('error: %s' % x)
			return

		cListen.listen(1)
		cListen.settimeout(5)

		try:
			c, a= cListen.accept()
		except Exception as x:
			print('error: %s' % x)
			return

		self.tcpSocket= c

		return True



	def send(self, _data):
		try:
			self.tcpSocket.send(_data)
			return True
		except:
			None



	'''
	Close socket.
	If called while running, cause exception in sending data,
	 resulting stop execution.
	'''
	def close(self):
		if not self.tcpSocket:
			return

		self.tcpSocket.close()



	'''
	Normal execution after caller is connected.
	Terminated by closed socket.
	'''
	def check(self):
		while True:
			#check port state
			if not self.send(b''):
				print('closed')
				return

			fileNew= self.detectActiveFile()

			if fileNew:
				if not self.camAirStart(fileNew):
					return
			YiAgent.time.sleep(.5)

		return



	'''
	Return file assumed to be currently recorded in Loop mode.
	That is file with specific name, updated recently.
	'''
	def detectActiveFile(self):
		mp4Mask= "%s/%s" % (self.camRoot, self.camMask)

		lastStamp= 0
		activeFile= None
		
		for mp4File in YiAgent.glob.glob(mp4Mask):
			mtime= YiAgent.os.path.getmtime(mp4File)
			
			if mtime>lastStamp:
				lastStamp= mtime
				activeFile= mp4File

		if not activeFile:
			return

		if YiAgent.time.time()-lastStamp > self.liveOldAge: #too old
			return

		fSize= YiAgent.os.path.getsize(activeFile)

		if fSize < self.liveTriggerSize: #too small
			return

		return {'fname': activeFile, 'size':fSize}



	'''
	start to read files from _file,
	assuming it's Loop mode (file name is Laaabbbb.MP4)
	'''
	def camAirStart(self, _file):
		fNameMatch= self.camMaskRe.match(_file['fname'])
		fParts= {'dir':int(fNameMatch.group('dir')), 'seq':int(fNameMatch.group('seq')), 'num':int(fNameMatch.group('num'))}

		fName= self.buildName(fParts)
		fPos= max( _file['size']-self.livePrefetch, 0)

		if not self.send('try: %s, %s' % (fName,fPos)):
			return
		return True



	def buildName(self, _fParts):
		return '%03dMEDIA/L%03d0%03d.MP4' % (_fParts['dir'], _fParts['seq'], _fParts['num'])



	def xxx(self):
		f= open('/dev/random', 'rb')
		
		block= 100000
		for n in range(10):
			b= f.read(block)
			
			if not self.send(b):
				print('stop')
				return

			if len(b)<block:
				break









	'''
	Test function.
	'''
	def test(self):
		YiAgent.threading.Timer(10, self.close).start()


		f= open('/dev/random', 'rb')
		
		block= 100000
		while True:
			b= f.read(block)
			
			if not self.send(b):
				print('stop')
				return

			if len(b)<block:
				break
