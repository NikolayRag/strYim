import sublime, sublime_plugin
import threading


from .kiTelnet import *

class YiCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		self.yiTelnet= KiTelnet('192.168.42.1', 'root')

		def YiCall():
			def cbYiRead(_iIn):
				parint(len(_iIn))
	#			print ('Yi ' +str(len(_iIn)) +' in, ' +str(aa[0]) +' total')




			_readPath='/tmp/fuse_d/DCIM/102MEDIA'
			_readName='L0080233.MP4'
			_readStart=000000
			_readLen=0
			req= {'readPath':_readPath, 'readName':_readName, 'readStart':_readStart+1, 'readLen':_readLen}


			res1= self.yiTelnet.command("ls -l %s" % _readPath, cbYiRead)

			res2= self.yiTelnet.command("ls -l /bin")
#			self.yiTelnet.command("tail -c +%(readStart)s %(readPath)s/%(readName)s | head -c %(readLen)s" % req, cbYiRead, True)
#			self.yiTelnet.command("tail -c +%(readStart)s %(readPath)s/%(readName)s" % req, cbYiRead, True)

			print("Yi->\n", res1, "\n<-Yi", res2)


		threading.Timer(0, YiCall).start()
