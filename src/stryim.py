import subprocess, threading, time, socket

class streamFFRTMP():
	tcp= None
	tcpSock= None
	h264Head= {
		(1080,30,'low'): b'\x00\x00\x00\x01\'M@3\x9ad\x03\xc0\x11?,\x8c\x04\x04\x05\x00\x00\x03\x03\xe9\x00\x00\xea`\xe8`\x00\xb7\x18\x00\x02\xdcl\xbb\xcb\x8d\x0c\x00\x16\xe3\x00\x00[\x8d\x97ypxD"R\xc0\x00\x00\x00\x01(\xee8\x80'
	}

	initFlag= None


	def __init__(self):
		self.tcp= None


		self.initFlag= threading.Event()

		ffport= 2345
		threading.Timer(0, lambda: self.tcpInit(ffport)).start()
		threading.Timer(0, lambda: self.serverInit(ffport)).start()

		self.initFlag.wait();


	def serverInit(self, _ffport):
		subprocess.call('D:/yi/restore/ff/ffmpeg -re -i tcp://localhost:%d -vcodec copy -f flv rtmp://localhost:5130/live/yi/' % _ffport, shell=False)


	def tcpInit(self, _ffport):
		self.tcpSock= socket.socket()

		self.tcpSock.bind(('127.0.0.1',_ffport))

		self.tcpSock.listen(1)
		self.tcp, a= self.tcpSock.accept()

		self.tcp.sendall(self.h264Head[(1080,30,'low')])

		self.initFlag.set()


	def go(self, _atom, _data):
		if self.tcp and _atom['type']=='H264':
			self.tcp.sendall(b'\x00\x00\x00\x01' +_data[4:])


	def stop(self):
		tcp= self.tcp
		self.tcp= None
		tcp.close()

		self.tcpSock.close()








import sublime, sublime_plugin
from .mp4RecoverExe import *
from .byteTransit import *
from .kiYiListener import *
from .kiTelnet import *
from .kiLog import *


KiYi= [None, None]

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


		kiLog.states(True, True, True)
		kiLog.states(False, False, True, 'KiYiListener')

		if KiYi[0]:
			kiLog.warn('Already')
			return

		selfIP= KiTelnet.defaults(address='192.168.42.1')
		

		KiYi[1]= streamFFRTMP()

		restoreO= mp4RecoverExe(KiYi[1].go)
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

		KiYi[1].stop()
