from .kiTelnet import *
from .kiSupport import *
import time, re
import threading




class KiYiListener():
	camRoot='/tmp/fuse_d/DCIM'
	camMask='*/L???????.MP4'

	detectTimeGap= 5 #maximum number of seconds to consider tested file 'live'

	reLsMask= re.compile('^(?P<rights>[^\s]+)\s+(?P<links>[^\s]+)\s+(?P<owner>[^\s]+)\s+(?P<group>[^\s]+)\s+(?P<size>[^\s]+)\s+(?P<date>[\w]+\s[\w]+\s[\d]+\s\d\d:\d\d:\d\d \d\d\d\d)\s+(?P<fname>.*)\s*$')


	aa= [0]
	yiTelnet= None
	flagRun= False

	def __init__(self):
		self.yiTelnet= KiTelnet('192.168.42.1', 'root')
		self.yiTelnet.logMode(False)

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

		detectedFile= None
		delayCheck= 1
		while self.flagRun:
			testFile= self.detectActiveFile(detectedFile)
			if getA(testFile,'live') and not getA(detectedFile,'live'):
				delayCheck= 10 #give more time
				print('On air: ', testFile)

			if not getA(testFile,'live') and getA(detectedFile,'live'):
				delayCheck= 1
				print('Off air')

			detectedFile= testFile


			time.sleep(delayCheck)

		print('enough Yi')



#		req= {'readPath':readPath, 'readName':readName, 'readStart':readStart+1, 'readLen':readLen}

#		self.aa= [0]
#		res2= self.yiTelnet.command("tail -c +%(readStart)s %(readPath)s/%(readName)s | head -c %(readLen)s" % req, self.cbYiRead, True)
#			res2= self.yiTelnet.command("tail -c +%(readStart)s %(readPath)s/%(readName)s" % req, self.cbYiRead, True)

#		print(self.aa[0])


#	def cbYiRead(self, _iIn):
#		self.aa[0]+=len(_iIn)









	'''
	called in cycle using self return value, search for currently "active" file.
	successfull file is defined by 'live' boolean field
	'''
	def detectActiveFile(self, _testFile=None):
		telnetResA= self.yiTelnet.command("ls -e -R -t %(root)s/%(mask)s |head -n 1; date" % {'root':self.camRoot, 'mask':self.camMask})
		telnetResA= telnetResA.split("\n") #'file \n date' retured

		camFileRe= self.reLsMask.match(telnetResA[0])
		if not camFileRe:
			return False


		camFile= camFileRe.groupdict()

		camTime= time.mktime( time.strptime(telnetResA[1], '%a %b %d %H:%M:%S UTC %Y') )
		camFileTime= time.mktime( time.strptime(camFile['date']) )
		camFile['age']= camTime-camFileTime
		camFile['live']= False

		
		if camFile['age']>self.detectTimeGap:
			return


		#compare with probably previous version
		if (
				getA(_testFile,'fname')==getA(camFile,'fname')
			and getA(_testFile,'size')<getA(camFile,'size')
		):
			camFile['live']= True

		return camFile

