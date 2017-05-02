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
	import threading, time, os, glob, re
	global threading, time, os, glob, re


	camRoot= '/tmp/fuse_d/DCIM'
	camMask= '???MEDIA/L???????.MP4'
	camMaskRe= re.compile('^.*(?P<dir>\d\d\d)MEDIA/L(?P<seq>\d\d\d)(?P<num>\d\d\d\d).MP4$')

	liveOldAge= 5 #maximum number of seconds to consider tested file 'live'
	liveTriggerSize= 1000000 #minimum file size to start reading
	livePrefetch= 1500000 #file shorter than this will be started from 0


	yiSock= None


	def __init__(self, _port, _test=None):
		self.yiSock= YiSock(_port)

		if not self.yiSock.valid():
			return

		if _test:
			self.test()
		else:
			self.check()



	'''
	Normal execution after caller is connected.
	Terminated by closed socket.
	'''
	def check(self):
		while True:
			#Check port state while record is paused.
			if not self.yiSock.valid(True):
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
			
			fileRes= self.camReadFile(fParts, fPos, fPartsExpect)
			if fileRes==-1:
				return

			if fileRes==0: 
				if not self.yiSock.send(None, 0):
					return

				return True

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


		with open('%s/%s' % (self.camRoot, fName), 'rb') as f:
			f.seek(_fPos)


			blankTry= 0
			while True:
				content= f.read()

				if content:
					blankTry= 0
					if not self.yiSock.send(content, _fParts['num']):
						return -1

					continue


				if blankTry>25: #5 sec
					return 0

				blankTry+= 1
				time.sleep(.2)


				fNext= '%s/%s' % (self.camRoot, fNameExpect)
				
				#next file created recently
				if (
					os.path.isfile(fNext)
					and time.time()-os.path.getmtime(fNext) < self.liveOldAge
				):
					return 1








	'''
	Test function.
	'''
	def test(self):
		threading.Timer(10, self.yiSock.close).start()


		f= open('/dev/random', 'rb')
		
		block= 100000
		while True:
			b= f.read(block)
			
			if not self.yiSock.send(b):
				print('stop')
				return

			if len(b)<block:
				break
