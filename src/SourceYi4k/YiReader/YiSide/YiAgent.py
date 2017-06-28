'''
Continuously detect loop-recorded files as soon as record is on.
Then read files as they grow and sequentally switch to next in chain.
Read data is send over accepted connection.
When Loop sequence is ended, next loop is waited for,
 and streaming continues.

Agent can be stopped from client by closing connection.

Agent is run at Yi4k side fully autonomously.
It is blocked at start until connection from client is made (only one).

Flow:
* accept connection
* continouosly detect file being recorded
* read tail
	* till next file in queue is recorded
		* repeat read
'''
class YiAgent():
	import threading, time, os, glob, re
	global threading, time, os, glob, re


	camRoot= '/tmp/SD0/DCIM'
	camMaskA= ['???MEDIA/L???????.MP4', '???MEDIA/YDXJ????.MP4', '???MEDIA/YN??????.MP4']
	camMaskRe= re.compile('^.*(?P<dir>\d\d\d)MEDIA/((?P<typeL>L)(?P<seqL>\d\d\d)|(?P<typeF>Y[DN])(XJ|(?P<seqF>\d\d)))(?P<num>\d\d\d\d).MP4$')

	liveOldAge= 5 #maximum number of seconds to consider tested file 'live'
	liveBlock= 512*1024 #read/send block size
	liveTriggerSize= 512*1024 #minimum file size to start reading
	livePrefetch= 2*512*1024 #file shorter than this will be started from 0

	tailBuffer= 0
	triggerOverflow= 8*512*1024 #chunk collected over this length considered overflow and skipped

	yiSock= None

	clean= None



	def __init__(self, _port):
		self.yiSock= YiSock(_port)

		self.clean= YiCleanup()



	'''
	Normal execution after caller is connected.
	Terminated by closed socket.
	'''
	def check(self):
		while self.yiSock.valid():	#Check port state while record is paused.
			fileNew= self.detectActiveFile()
			if fileNew:
				fNameMatch= self.camMaskRe.match(fileNew['fname'])
				if not fNameMatch:
					continue


				fPos= max( fileNew['size']-self.livePrefetch, 0)

				if fNameMatch.group('typeL'):
					fParts= {'fname':fileNew['fname'], 'dir':int(fNameMatch.group('dir')), 'seq':int(fNameMatch.group('seqL')), 'num':int(fNameMatch.group('num'))}
					incFn= self.incLoop

				if fNameMatch.group('typeF'):
					fParts= {'fname':fileNew['fname'], 'dir':int(fNameMatch.group('dir')), 'seq':int(fNameMatch.group('seqF')), 'num':int(fNameMatch.group('num'))}
					incFn= self.incFlat

				if not self.startChain(fParts, fPos, incFn):
					break


				if not self.yiSock.send():	#reset context
					break

			time.sleep(.5)


		self.clean.fire(True)

		os.remove(__file__) #kill self


	'''
	Return file assumed to be currently recorded in Loop mode.
	That is file with specific name, updated recently.
	'''
# -todo 270 (YiAgent, clean) +0: detect only file which grown in current session
	def detectActiveFile(self):
		lastStamp= 0
		activeFile= None
		
		for cMask in self.camMaskA:
			for mp4File in glob.glob("%s/%s" % (self.camRoot, cMask)):
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
	using _incFn function to increment file in chain
	'''
	def startChain(self, _fParts, _fPos, _incFn):
		while True:
			fPartsExpect= _incFn(_fParts)

			fileRes= self.readFile(_fParts['fname'], _fPos, _fParts['num'], fPartsExpect['fname'])
			if fileRes==-1:
				return

			if fileRes==None: 
				return True

			_fParts= fPartsExpect
			_fPos= 0



	def incLoop(self, _fParts):
		newParts= {'dir':_fParts['dir'], 'seq':_fParts['seq'], 'num':_fParts['num']}

		newParts['num']+= 1
		if newParts['num']==1000:
			newParts['num']= 1
			newParts['dir']+= 1

		newParts['fname']= '%s/%03dMEDIA/L%03d0%03d.MP4' % (self.camRoot, newParts['dir'], newParts['seq'], newParts['num'])

		return newParts



	def incFlat(self, _fParts):
		newParts= {'dir':_fParts['dir'], 'seq':_fParts['seq'] or 0, 'num':_fParts['num']}

		newParts['seq']+= 1

		newParts['fname']= "%s/%03dMEDIA/YN%02d0%03d.MP4" % (self.camRoot, newParts['dir'], newParts['seq'], newParts['num'])

		return newParts



	'''
	Read file untill it's exhausted.
	That is until expected file arrives and current file returns 0 bytes.
	'''
	def readFile(self, _fName, _fPos, _ctx=1, _fNameExpect=None):
		self.yiSock.msgLog(_fName)

		blankTry= 0
		with open(_fName, 'rb') as f:
			self.clean.add(_fName)

			while self.yiSock.valid():
				readAmt= self.readBlock(f, _fPos, self.tailBuffer, _ctx)
				if readAmt==-1:
					return -1

				if readAmt:
					_fPos+= readAmt
					blankTry= 0

					continue


				if blankTry>25: #5 sec
					break

				blankTry+= 1
				time.sleep(.2)


				if _fNameExpect:
					if (
						os.path.isfile(_fNameExpect)
						and time.time()-os.path.getmtime(_fNameExpect) < self.liveOldAge
					): #next file created recently
						self.readBlock(f, _fPos, 0, _ctx) #get remaining stuff

						return 1




	'''
	Read available data from file and send it to host in cycle.
	Some data can be left.
	'''
	def readBlock(self, _f, _pos, _leave=0, _ctx=0):
		_f.seek(0, os.SEEK_END)
		fRemain= _f.tell() -_pos -_leave

		if fRemain>self.triggerOverflow:
			self.yiSock.msgOverflow(fRemain)
			return 0


		_f.seek(_pos)

		fBlock= fRemain
		while fBlock>0:
			amt= min(fBlock,self.liveBlock)

			content= _f.read(amt)
			if not self.yiSock.send(content, _ctx):
				return -1

			fBlock-= amt


		return fRemain







	'''
	Test function.
	'''
	def testRandom(self):
		if not self.yiSock.valid():
			return


		threading.Timer(1, self.yiSock.close).start()


		f= open('/dev/random', 'rb')
		
		block= 100000
		while True:
			b= f.read(block)
			
			if not self.yiSock.send(b):
				return

			if len(b)<block:
				break



	def testClean(self):
		clean= YiCleanup()
		clean.add('/tmp/fuse_d/DCIM/115MEDIA/L0890127.MP4')
		clean.add('/tmp/fuse_d/DCIM/115MEDIA/L0890128.MP4')
		clean.fire()
