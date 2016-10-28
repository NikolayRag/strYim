import sublime, sublime_plugin
import threading


from .kiTelnet import *

class YiCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		self.yiTelnet= KiTelnet('192.168.42.1', 'root')

		aa= [0]
		def YiCall():
			def cbYiRead(_iIn):
				aa[0]+=len(_iIn)




			_readPath='/tmp/fuse_d/DCIM'
			_mask='L???????.MP4'
			_readName='L0110243.MP4'
			_readStart=60000000
			_readLen=10000000
			req= {'readPath':_readPath, 'readName':_readName, 'readStart':_readStart+1, 'readLen':_readLen}


			res= self.yiTelnet.command("ls -e -R -t %s" % _readPath)
			print("Yi->\n%s\n<-Yi" % res)

			aa= [0]
			res2= self.yiTelnet.command("tail -c +%(readStart)s %(readPath)s/%(readName)s | head -c %(readLen)s" % req, cbYiRead, True)
#			res2= self.yiTelnet.command("tail -c +%(readStart)s %(readPath)s/%(readName)s" % req, cbYiRead, True)

			print(aa[0])


		threading.Timer(0, YiCall).start()
