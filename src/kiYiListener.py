from .kiTelnet import *
from .kiSupport import *
import time, re
import threading




class KiYiListener():
	camRoot='/tmp/fuse_d/DCIM'
	camMask='*/L???????.MP4'

	detectTimeGap= None #maximum number of seconds to consider tested file 'live'

	reLsMask= re.compile('^(?P<rights>[^\s]+)\s+(?P<links>[^\s]+)\s+(?P<owner>[^\s]+)\s+(?P<group>[^\s]+)\s+(?P<size>[^\s]+)\s+(?P<date>[\w]+\s[\w]+\s[\d]+\s\d\d:\d\d:\d\d \d\d\d\d)\s+(?P<fname>.*)\s*$')


	aa= [0]
	yiTelnet= None
	flagRun= False

	def __init__(self, _maxAge=4):
		self.detectTimeGap= _maxAge

		self.flagRun= False


	def run(self):
		if self.flagRun:
			print('not twice')
			return

		self.flagRun= True
		threading.Timer(0, self.YiListen).start()


	def stop(self):
		self.flagRun= False



	'''
	wait for live recording and seamlessly read it chained untill and 
	'''
	def YiListen(self):
		print('listen to Yi')

		self.yiTelnet= KiTelnet('192.168.42.1', 'root')
		self.yiTelnet.logMode(False)

		testFileOld= None
		while self.flagRun:
			testFileNew= self.detectActiveFile()
			
			if testFileNew and not testFileOld:
				print('On air: ', testFileNew)

			if testFileOld and not testFileNew:
				print('Off air')

			testFileOld= testFileNew

			time.sleep(1)

		print('enough Yi')

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
		telnetResA= self.yiTelnet.command("ls -e -R -t %(root)s/%(mask)s |head -n 1; date" % {'root':self.camRoot, 'mask':self.camMask})
		if not telnetResA:
			return False
		telnetResA= telnetResA.split("\n") #'file \n date' retured

		camFileRe= self.reLsMask.match(telnetResA[0])
		if not camFileRe:
			return False


		camFile= camFileRe.groupdict()

		camTime= time.mktime( time.strptime(telnetResA[1], '%a %b %d %H:%M:%S UTC %Y') )
		camFileTime= time.mktime( time.strptime(camFile['date']) )
		camFile['age']= camTime-camFileTime

		
		if camFile['age']<=self.detectTimeGap:
			return camFile
























import sublime, sublime_plugin
import threading

#from .kiYiListener import *


KiYi= [None]

class YiOnCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if not KiYi[0]:
			KiYi[0]= KiYiListener()
		KiYi[0].run()


class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if KiYi[0]:
			KiYi[0].stop()
