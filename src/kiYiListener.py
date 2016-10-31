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
	kiLog.prefixes(
	      'YiListen log:'
	    , 'YiListen warning:'
	    , 'YiListen ERROR:'
	)



	reLsMask= re.compile('^(?P<rights>[^\s]+)\s+(?P<links>[^\s]+)\s+(?P<owner>[^\s]+)\s+(?P<group>[^\s]+)\s+(?P<size>[^\s]+)\s+(?P<date>[\w]+\s[\w]+\s[\d]+\s\d\d:\d\d:\d\d \d\d\d\d)\s+(?P<fname>.*)\s*$')

	camIP= '192.168.42.1'
	camUser= 'root'
	camPass= ''
	camRoot= '/tmp/fuse_d'
	camMask= '???MEDIA/L???????.MP4'

	detectTimeGap= 4 #maximum number of seconds to consider tested file 'live'


	flagRun= False
	camLive= False
	goAir= True


	def __init__(self):
		kiLog.states(
		      False
		    , False
		    , False
		    , 'KiTelnet'
		)

		KiTelnet.defaults(self.camIP, self.camUser, self.camPass, 8088)


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





	def checkTriger(self, _fOld, _fNew):
		if _fOld==False and _fNew!=False:
			kiLog.ok('connected')

		if _fNew and not _fOld:
			self.camLive= True
			kiLog.ok('found: %s' % _fNew)

		if _fOld and _fNew and _fNew!=_fOld:
			kiLog.ok('refresh: %s' % _fNew)

		if _fOld and not _fNew:
			self.camLive= False
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

			if self.goAir and self.camLive:
				kiLog.warn('ON AIR')
#				self.camRead(fileNew)
				kiLog.warn('OFF AIR')

			time.sleep(1)


		kiLog.ok('stop')

#  todo 16 (clean, network) +0: cleanup unneeded KiTelnet at stop()



#		req= {'readPath':readPath, 'readName':readName, 'readStart':readStart+1, 'readLen':readLen}

#		self.aa= [0]
#		res2= self.yiTelnet.command("tail -c +%(readStart)s %(readPath)s/%(readName)s | head -c %(readLen)s" % req, self.cbYiRead, True)
#			res2= self.yiTelnet.command("tail -c +%(readStart)s %(readPath)s/%(readName)s" % req, self.cbYiRead, True)

#		print(self.aa[0])


#	def cbYiRead(self, _iIn):
#		self.aa[0]+=len(_iIn)





	'''
	called in cycle using self return value, search for currently "actual" file.
	'''
	def detectActiveFile(self):
		yiTelnet= KiTelnet("cd %s/DCIM/; ls -e -R -t %s |head -n 1; date" % (self.camRoot, self.camMask))
		telnetResA= yiTelnet.result()
		if telnetResA==False: #error
			return False
		telnetResA= telnetResA.split("\n") #'file \n date' retured

		camFileRe= self.reLsMask.match(telnetResA[0])
		if not camFileRe: #mismatch result
			return


		camFile= camFileRe.groupdict()

		camTime= time.mktime( time.strptime(telnetResA[1], '%a %b %d %H:%M:%S UTC %Y') )
		camFileTime= time.mktime( time.strptime(camFile['date']) )
		camFile['age']= camTime-camFileTime

		
		if camFile['age']>self.detectTimeGap: #too old
			return
			
		return {'fname': camFile['fname'], 'size': camFile['size']}
























import sublime, sublime_plugin
import threading

#from .kiYiListener import *


KiYi= [None]

class YiOnCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if KiYi[0]:
			kiLog.warn('Already')
			return

		KiYi[0]= KiYiListener()


class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if KiYi[0]:
			KiYi[0].stop()
			KiYi[0]= None

