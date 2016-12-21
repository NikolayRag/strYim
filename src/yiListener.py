import time, re, threading

from .kiTelnet import *
from .kiSupport import *
from .kiLog import *




'''
connect to Yi and get live file
reconnect if needed
'''
class YiListener():
	lsMaskRe= re.compile('^(?P<rights>[^\s]+)\s+(?P<links>[^\s]+)\s+(?P<owner>[^\s]+)\s+(?P<group>[^\s]+)\s+(?P<size>[^\s]+)\s+(?P<date>\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)\s+(?P<fname>.*)\s*$')

	camRoot= '/tmp/fuse_d/DCIM'
	camMask= '???MEDIA/L???????.MP4'
	camMaskRe= re.compile('^(?P<dir>\d\d\d)MEDIA/L(?P<seq>\d\d\d)(?P<num>\d\d\d\d).MP4$')

	liveOldAge= 4 #maximum number of seconds to consider tested file 'live'
	liveTriggerSize= 1000000 #minimum file size to start reading
	livePrefetch= 15000000 #file shorter than this will be started from 0

	flagLive= False #live switch
	flagRun= False #global cycle switch

	connectCB= None
	liveCB= None
	airCB= None
	mp4CB= False


	def __init__(self):
		None



	'''
	Begin to look at camera state.
	This is neccessary for live() to start.

		connectCB
			callback for connection state,
			True or False is passed in as a state

		liveCB
			callback for camera shooting detection,
			passed in value of:
				1
					camera begin to shoot
				0
					camera continue to shoot seamlessly (in loop mode)
				-1
					camera stops shooting

		deadCB
			called when listener loop is finally over.
			This is done eventually after calling .stop(),
				delayed for read stream to fe flushed down to the recoverer.
			YiListener object instance is no more usable after that.
	'''
	def start(self, _connectCB=None, _liveCB=None, _deadCB= None):
		if self.flagRun:
			kiLog.warn('Already running')
			return

		self.connectCB= _connectCB
		self.liveCB= _liveCB
		self.deadCB= _deadCB
		self.flagRun= True

		threading.Timer(0, self.check).start()


	def stop(self):
		self.dead()

		self.flagRun= False



	'''
	attempt to start streaming to mp4CB.

		mp4CB(bytes data, context=None)
			 function for which to stream mp4 content

		airCB
			callback, called with
				1
					for actually start streaming
				0
					when streaming ends normally (by demand)
				-1
					when streaming error occurs
	'''
	def live(self, _mp4CB, _airCB=None):
		if not self.flagRun:
			kiLog.warn('Listener is currently idle')
			return

		if self.flagLive:
			kiLog.warn('Already live')
			return

		self.mp4CB= _mp4CB
		self.airCB= _airCB
		self.flagLive= True

	def dead(self):
		self.flagLive= False




	def checkTriger(self, _fOld, _fNew):
		if _fOld==False and _fNew!=False:
			kiLog.ok('connected')
			callable(self.connectCB) and self.connectCB(True)

		if _fNew and not _fOld:
			kiLog.ok('found: %s' % _fNew)
			callable(self.liveCB) and self.liveCB(1)

		if _fOld and _fNew and _fNew['fname']!=_fOld['fname']:
			kiLog.ok('refresh: %s' % _fNew)
			callable(self.liveCB) and self.liveCB(0)

		if _fOld and not _fNew:
			kiLog.ok('lost')
			callable(self.liveCB) and self.liveCB(-1)

		if _fOld!=False and _fNew==False:
			kiLog.err('disconnected')
			callable(self.connectCB) and self.connectCB(False)



	'''
	(re)connect to Yi
	Initial state is error.
	'''
	def check(self):
		kiLog.ok('start')

		fileNew= fileOld= False
		while self.flagRun:
			fileOld= fileNew
			fileNew= self.detectActiveFile()
			self.checkTriger(fileOld, fileNew)

			if (
				self.flagLive
				and fileNew
				and fileNew['size'] > self.liveTriggerSize
			):
				kiLog.ok('ON AIR')
				callable(self.airCB) and self.airCB(1)

				if self.camAirStart(fileNew):
					kiLog.ok('OFF AIR')
					callable(self.airCB) and self.airCB(0)
				else:
					kiLog.err('BAD AIR')
					callable(self.airCB) and self.airCB(-1)

				self.mp4CB(None,None) #reset


			time.sleep(1)


		kiLog.ok('stop')

		callable(self.deadCB) and self.deadCB()





	def buildName(self, _fParts):
		return '%sMEDIA/L%s0%s.MP4' % (pad(_fParts['dir'],3), pad(_fParts['seq'],3), pad(_fParts['num'],3))


	'''
	start to read files from _file,
	assuming it's Loop mode (file name is Laaabbbb.MP4)
	'''
	def camAirStart(self, _file):
		stamp= time.time()

		fNameMatch= self.camMaskRe.match(_file['fname'])
		if not fNameMatch:
			return False
		fParts= {'dir':int(fNameMatch.group('dir')), 'seq':int(fNameMatch.group('seq')), 'num':int(fNameMatch.group('num'))}


		fName= self.buildName(fParts)
		fPos= max( _file['size']-self.livePrefetch, 0)

#  todo 33 (read, cam) +0: detect buffer overrun
#  todo 34 (read, cam) +0: detect buffer underrun
		while True:
			kiLog.ok('Read %s from %d ...' % (fName, fPos))
			while True:
# -todo 114 (read, cam) +0: define maximum read block
				if not self.flagLive:
					kiLog.warn("... stop at %d" % fPos)
					return True #stopped by demand

				self.mp4CB(None,'%s_%s' % (pad(fParts['dir'],3), pad(fParts['num'],4)))
				readBytes= self.camReadFile(fName, fPos)

				if readBytes==-1:
					kiLog.err("... error at %d" % fPos)
					return False

				if not readBytes: #no more, move to next
					break

				fPos+= readBytes

				time.sleep(.5)


# =todo 31 (read, cam) +1: check 999+ file switch
			fParts['num']= (fParts['num'] +1) %1000
			if fParts['num']==0:
				fParts['dir']+= 1

			fName= self.buildName(fParts)

			#current file dried but no next one
			checkNext= KiTelnet("ls %s/%s" % (self.camRoot, fName)).result()
			if not checkNext:
				kiLog.warn("... finish at %d" % fPos)
#  todo 68 (cam, stability) -1: found other way to forget stopped file as live
				time.sleep(self.liveOldAge-1) #wait till stopped file will get old to not treat it as live at next cycle
				return True #stopped by camera

			kiLog.ok("... to %d" % fPos)

			fPos= 0



#  todo 53 (cam) +0: force kill data sending at dead()
	'''
	read specified file from start position till (current) end.
	'''
	def camReadFile(self, _fname, _start):
		ddBlock= 1000000
		ddSkipBlocks= int(_start /ddBlock)
		skipBuffer= _start %ddBlock #bytes to skip, len

		telCmd= "dd bs=%d skip=%d if=%s/%s |tail -c +%d" % (ddBlock, ddSkipBlocks, self.camRoot, _fname, skipBuffer+1)
		return KiTelnet(telCmd, self.mp4CB).result()








	'''
	called in cycle using self return value, search for currently "actual" file.
	'''
	def detectActiveFile(self):
		telCmd= "cd %s/; ls -e -R -t %s |head -n 1; date" % (self.camRoot, self.camMask)
		telnetResA= KiTelnet(telCmd).result()
		if telnetResA==-1: #error
			return False
		telnetResA= telnetResA.decode('ascii').split("\n") #'file \n date' retured

		camFileMatch= self.lsMaskRe.match(telnetResA[0])
		if not camFileMatch: #mismatch result
			return


		camFileMatch= camFileMatch.groupdict()

		camTime= time.mktime( time.strptime(telnetResA[1], '%a %b %d %H:%M:%S UTC %Y') )
		camFileTime= time.mktime( time.strptime(camFileMatch['date']) )
		camFileMatch['age']= camTime-camFileTime

		if camFileMatch['age']>self.liveOldAge: #too old
			return
			
		return {'fname': camFileMatch['fname'], 'size': int(camFileMatch['size'])}

