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



	'''
	(re)connect to Yi
	'''
	def check(self):
		kiLog.ok('Listening')

		testFileOld= ''
		while self.flagRun:
			time.sleep(1)

			testFileNew= self.detectActiveFile()

			if testFileOld!=False and testFileNew==False:
				kiLog.err('while listening')

			if testFileNew and not testFileOld:
				kiLog.ok('On air: %s' % testFileNew)

			if testFileOld and not testFileNew:
				kiLog.ok('Off air')

			if testFileOld and testFileNew and testFileNew!=testFileOld:
				kiLog.ok('Fresh air: %s' % testFileNew)


			testFileOld= testFileNew

		kiLog.ok('Unlistening')

# -todo 16 (clean, network) +0: cleanup unneeded KiTelnet at stop()



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
			return ''


		camFile= camFileRe.groupdict()

		camTime= time.mktime( time.strptime(telnetResA[1], '%a %b %d %H:%M:%S UTC %Y') )
		camFileTime= time.mktime( time.strptime(camFile['date']) )
		camFile['age']= camTime-camFileTime

		
		if camFile['age']<=self.detectTimeGap:
			return camFile['fname']
























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

