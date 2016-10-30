from .kiTelnet import *
from .kiSupport import *
import time, re
import threading



'''
connect to Yi and get live file
reconnect if needed
'''
class KiYiListener():


	reLsMask= re.compile('^(?P<rights>[^\s]+)\s+(?P<links>[^\s]+)\s+(?P<owner>[^\s]+)\s+(?P<group>[^\s]+)\s+(?P<size>[^\s]+)\s+(?P<date>[\w]+\s[\w]+\s[\d]+\s\d\d:\d\d:\d\d \d\d\d\d)\s+(?P<fname>.*)\s*$')

	camIP= '192.168.42.1'
	camUser= 'root'
	camPass= ''
	camRoot= '/tmp/fuse_d'
	camMask= '???MEDIA/L???????.MP4'

	detectTimeGap= 4 #maximum number of seconds to consider tested file 'live'


	flagRun= False




	'''
	support for telnet
	'''
	def telnet(self, _command, _cb=None, _block=True):
		yiTelnet= KiTelnet(self.camIP, self.camUser, self.camPass, _command, _cb)
		if _block:
			return yiTelnet.result()




	def __init__(self):
		self.flagRun= False

		self.start()




	def start(self):
		if self.flagRun:
			print('not twice')
			return

		self.flagRun= True

		threading.Timer(0, self.check).start()


	def stop(self):
		self.flagRun= False



	'''
	(re)connect to Yi
	'''
	def check(self):
		if not self.yiCheck():
			print('No proper Yi found')
			return
		print('Listening Yi')

		testFileOld= ''
		while self.flagRun:
			time.sleep(1)

			testFileNew= self.detectActiveFile()

			if testFileNew==False:
				print('Yi Error')
				testFileOld= '' #reset
				continue

			if testFileNew and not testFileOld:
				print('On air: ', testFileNew)

			if testFileOld and not testFileNew:
				print('Off air')


			testFileOld= testFileNew

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
	check if specified telnet belongs to Yi
	'''
	def yiCheck(self):
		#list path and listen only for errors
		if self.telnet("(ls %s |head -n 0) 2>&1" % self.camRoot) == "":
			return True




	'''
	called in cycle using self return value, search for currently "actual" file.
	'''
	def detectActiveFile(self):
		telnetResA= self.telnet("ls -e -R -t %s/DCIM/%s |head -n 1; date" % (self.camRoot, self.camMask))
		if not telnetResA: #error
			return False
		telnetResA= telnetResA.split("\n") #'file \n date' retured

		camFileRe= self.reLsMask.match(telnetResA[0])
		if not camFileRe: #mismatch result
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
		if KiYi[0]:
			print('Already')
			return

		KiYi[0]= KiYiListener()


class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if KiYi[0]:
			KiYi[0].stop()
			KiYi[0]= None

