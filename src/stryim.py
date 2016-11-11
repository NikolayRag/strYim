import subprocess, threading, time, socket

class streamFFRTMP():
	def go(self):
		threading.Timer(0, lambda: subprocess.call('D:/yi/restore/ffmpeg -re -i tcp://localhost:2345 -vcodec copy -f flv rtmp://localhost:5130/live/yi/', shell=False)).start()
		
		tcpSock= socket.socket()

		tcpSock.bind(('127.0.0.1',2345))

		tcpSock.listen(1)
		c, a= tcpSock.accept()

		a=0
		while a<10:
			f= open('D:/yi/restore/stryim/tmp2.h264', 'rb')
			aa= f.read()
			f.close()

			c.sendall(aa)

			a+=1

		c.close()









import sublime, sublime_plugin
from .mp4RecoverExe import *
from .byteTransit import *
from .kiYiListener import *
from .kiTelnet import *
from .kiLog import *


KiYi= [None]

'''
YiOn/Off commands are used to test Stryim in Sublime, `coz its lazy to set up running environment.
'''
class YiOnCommand(sublime_plugin.TextCommand):
	def cbConn(self, _mode):
		kiLog.ok('Connected' if _mode else 'Disconnected')
	def cbLive(self, _mode):
		if _mode==1:
			kiLog.ok('Live')
		if _mode==-1:
			kiLog.ok('Dead')
	def cbAir(self, _mode):
		if _mode==1:
			kiLog.warn('Air On')
		if _mode==0:
			kiLog.warn('Air Off')
		if _mode==-1:
			kiLog.err('Air bad')

	def run(self, _edit):
		streamFFRTMP().go()
		return


		kiLog.states(True, True, True)
		kiLog.states(False, False, True, 'KiYiListener')

		if KiYi[0]:
			kiLog.warn('Already')
			return

		selfIP= KiTelnet.defaults(address='192.168.42.1')
		

		def abs(a, d):
#			print(a['ftype'],len(d))
			None
		restoreO= mp4RecoverExe(None)
		buffer= byteTransit(restoreO.parse, 1000000)



#		buffer.context('123')
#		KiTelnet('cat /tmp/fuse_d/DCIM/105MEDIA/L0010639.MP4', buffer.add).result()
#		buffer.context(None)
#		return



		KiYi[0]= KiYiListener()
		KiYi[0].start(self.cbConn, self.cbLive)
		KiYi[0].live(buffer, self.cbAir)


#ast.literal_eval(aa)
class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if not KiYi[0]:
			kiLog.warn('Already')
			return

		KiYi[0].stop()
		KiYi[0]= None

