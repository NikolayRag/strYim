'''
Continuously detect loop-recorded files as soon as record is on.
Then read files in chain as they grow and sequentally switched.
Read data is send over accepted connection.

Agent is run at Yi4k side.

Flow:
* continouosly detect file being recorded
* read tail
	* till next file in queue is recorded
		* repeat read
'''
class YiAgent():
	import socket, threading, time, os, glob, re
	global socket, threading, time, os, glob, re


	camRoot= '/tmp/fuse_d/DCIM'
	camMask= '???MEDIA/L???????.MP4'
	camMaskRe= re.compile('^.*(?P<dir>\d\d\d)MEDIA/L(?P<seq>\d\d\d)(?P<num>\d\d\d\d).MP4$')

	liveOldAge= 8 #maximum number of seconds to consider tested file 'live'
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
		cListen= socket.socket()
		cListen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
			#Check port state while record is paused.
			if not self.send(b''):
				return

			fileNew= self.detectActiveFile()

			if fileNew:
				if not self.camAirStart(fileNew):
					return
			time.sleep(.5)

		return



	'''
	Return file assumed to be currently recorded in Loop mode.
	That is file with specific name, updated recently.
	'''
	def detectActiveFile(self):
		mp4Mask= "%s/%s" % (self.camRoot, self.camMask)

		lastStamp= 0
		activeFile= None
		
		for mp4File in glob.glob(mp4Mask):
			mtime= os.path.getmtime(mp4File)
			
			if mtime>lastStamp:
				lastStamp= mtime
				activeFile= mp4File


		if not activeFile:
			return

		if time.time()-lastStamp > self.liveOldAge: #too old
			return

		fSize= os.path.getsize(activeFile)

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

		fPos= max( _file['size']-self.livePrefetch, 0)

		while True:
			fPartsExpect= self.incFile(fParts)
			
			if not self.camReadFile(fParts, fPos, fPartsExpect):
				return

			fParts= fPartsExpect
			fPos= 0


	def incFile(self, _fParts):
		newParts= {'dir':_fParts['dir'], 'seq':_fParts['seq'], 'num':_fParts['num']}

		newParts['num']+= 1
		if newParts['num']==1000:
			newParts['num']= 1
			newParts['dir']+= 1

		return newParts



	def buildName(self, _fParts):
		return '%03dMEDIA/L%03d0%03d.MP4' % (_fParts['dir'], _fParts['seq'], _fParts['num'])



	'''
	Read file untill it's exhausted.
	That is until expected file arrives and current file returns 0 bytes.
	'''
	def camReadFile(self, _fParts, _fPos, _fPartsExpect):
		fName= self.buildName(_fParts)
		fNameExpect= self.buildName(_fPartsExpect)

		if not self.send('%s from %d' % (fName,_fPos)):
			return

		f= open('%s/%s' % (self.camRoot, fName), 'rb')
		f.seek(_fPos)


		readResult= True
		while True:
			content= f.read()

			if content:
				_fPos+=len(content)
				if not self.send('+%d = %d' % (len(content), _fPos)):
					readResult= False
					break

			time.sleep(.5)

			fNext= '%s/%s' % (self.camRoot, fNameExpect)
			if (
				not content
				and os.path.isfile(fNext)
			):
				if time.time()-os.path.getmtime(fNext) < self.liveOldAge: #young ehough
					break




		f.close()

		return readResult










	'''
	Test function.
	'''
	def test(self):
		threading.Timer(10, self.close).start()


		f= open('/dev/random', 'rb')
		
		block= 100000
		while True:
			b= f.read(block)
			
			if not self.send(b):
				print('stop')
				return

			if len(b)<block:
				break
