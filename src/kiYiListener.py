import time, re
import threading

from .kiTelnet import *
from .kiSupport import *
from .kiLog import *




'''
connect to Yi and get live file
reconnect if needed
'''
class KiYiListener():
	lsMaskRe= re.compile('^(?P<rights>[^\s]+)\s+(?P<links>[^\s]+)\s+(?P<owner>[^\s]+)\s+(?P<group>[^\s]+)\s+(?P<size>[^\s]+)\s+(?P<date>\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)\s+(?P<fname>.*)\s*$')

	camIP= '192.168.42.1'
	camUser= 'root'
	camPass= ''
	camRoot= '/tmp/fuse_d'
	camMask= '???MEDIA/L???????.MP4'
	camMaskRe= re.compile('^(?P<dir>\d\d\d)MEDIA/L(?P<seq>\d\d\d)(?P<num>\d\d\d\d).MP4$')

	liveOldAge= 4 #maximum number of seconds to consider tested file 'live'
	liveBufferMin= 5000000 #bytes prefetch at file reading start
	ddBlock= 1000000

	flagLive= True #live switch
	flagRun= False #global cycle switch



	kiLog.states(
	      False
	    , False
	    , False
	    , 'KiTelnet'
	)

	KiTelnet.defaults(camIP, camUser, camPass, 8088)


	def __init__(self):
		self.flagRun= False

		self.start()




	def start(self):
		if self.flagRun:
			kiLog.warn('not twice')
			return

		self.flagRun= True

		threading.Timer(0, self.check).start()


	def stop(self):
		self.flagRun= False
		self.flagLive= False




	def checkTriger(self, _fOld, _fNew):
		if _fOld==False and _fNew!=False:
			kiLog.ok('connected')

		if _fNew and not _fOld:
			kiLog.ok('found: %s' % _fNew)

		if _fOld and _fNew and _fNew['fname']!=_fOld['fname']:
			kiLog.ok('refresh: %s' % _fNew)

		if _fOld and not _fNew:
			kiLog.ok('lost')

		if _fOld!=False and _fNew==False:
			kiLog.err('disconnected')



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
				and fileNew['size'] > self.liveBufferMin
			):
				kiLog.warn('ON AIR')
				if self.camAirStart(fileNew):
					kiLog.warn('OFF AIR')
				else:
					self.flagLive= False
					kiLog.err('BAD AIR')

			time.sleep(1)


		kiLog.ok('stop')




	def camAirStart(self, _file):
		stamp= time.time()

		fNameMatch= self.camMaskRe.match(_file['fname'])
		if not fNameMatch:
			return False
		fParts= {'dir':int(fNameMatch.group('dir')), 'seq':int(fNameMatch.group('seq')), 'num':int(fNameMatch.group('num'))}


		fPos= _file['size'] -self.liveBufferMin

		while True:
			fName= '%sMEDIA/L%s%s.MP4' % (pad(fParts['dir'],3), pad(fParts['seq'],3), pad(fParts['num'],4))
			kiLog.ok('Read %s from %d ...' % (fName, fPos))
			while True:
				if not self.flagLive:
					return True

				readBytes= self.camReadFile(fName, fPos)

				if readBytes==-1:
					return False

				if not readBytes:
					break

				fPos+= readBytes

				time.sleep(1)

			kiLog.ok("... to %d" % fPos)

			fPos= 0

# =todo 31 (read, cam) +0: check 999+ file switch
			fParts['num']= (fParts['num'] +1) %1000
			if fParts['num']==0:
				fParts['dir']+= 1


		return True


	'''
	read specified file from start position till (current) end.
	'''
	def camReadFile(self, _fname, _start):
		ddSkipBlocks= int(_start /self.ddBlock)

		skipBuffer= [_start-(ddSkipBlocks*self.ddBlock)] #bytes to skip, len
		self.readBuffer= 0
		def cbReadFile(_data):
			if skipBuffer[0]>0:
				skipBuffer[0]-= len(_data)
				if skipBuffer[0]>=0:
					return
				else:
					_data= _data[skipBuffer[0]:]

			self.readBuffer+= len(_data)

		telCmd= "dd bs=%d skip=%d if=%s/DCIM/%s" % (self.ddBlock, ddSkipBlocks, self.camRoot, _fname)
		if KiTelnet(telCmd, cbReadFile).result()==False:
			return -1
		return self.readBuffer








	'''
	called in cycle using self return value, search for currently "actual" file.
	'''
	def detectActiveFile(self):
		telCmd= "cd %s/DCIM/; ls -e -R -t %s |head -n 1; date" % (self.camRoot, self.camMask)
		telnetResA= KiTelnet(telCmd).result()
		if telnetResA==False: #error
			return False
		telnetResA= telnetResA.split("\n") #'file \n date' retured

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
























import sublime, sublime_plugin
import threading

#from .kiYiListener import *


KiYi= [None]

'''
YiOn/Off commands are used to test Stryim in Sublime, `coz its lazy to set up running environment.
'''
class YiOnCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if KiYi[0]:
			kiLog.warn('Already')
			return

		KiYi[0]= KiYiListener()


class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if not KiYi[0]:
			kiLog.warn('Already')
			return

		KiYi[0].stop()
		KiYi[0]= None

