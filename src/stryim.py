'''
Mux-suitable sink for sending binary data to file
'''
class SinkFile():
	cFile= None

	def __init__(self, _fn):
		self.cFile= open(_fn, 'wb')

	def add(self, _data):
		self.cFile.write(_data)

	def close(self):
		self.cFile.close()




'''
Mux-suitable sink for sending binary data to RTMP
'''
import subprocess, threading, socket
class SinkRTMP():
	tcp= None
	tcpSock= None

	initFlag= None


	def __init__(self):
		self.tcp= None


		self.initFlag= threading.Event()

		ffport= 2345
		threading.Timer(0, lambda: self.tcpInit(ffport)).start()
		threading.Timer(0, lambda: self.serverInit(ffport)).start()

		self.initFlag.wait();


	def serverInit(self, _ffport):
		None
		subprocess.call('D:/yi/restore/ff/ffmpeg -re -i tcp://localhost:%d -vcodec copy -f flv rtmp://localhost:5130/live/yi/' % _ffport, shell=False)
#		subprocess.call('D:/yi/restore/ff/ffmpeg -re -i tcp://localhost:%d -vcodec copy http://localhost:8090/yi.ffm' % _ffport, shell=False)


	def tcpInit(self, _ffport):
		self.tcpSock= socket.socket()

		self.tcpSock.bind(('127.0.0.1',_ffport))

		self.tcpSock.listen(1)
		self.tcp, a= self.tcpSock.accept()

		self.initFlag.set()


	def add(self, _data):
		if not self.tcp:
			return

		try:
			self.tcp.sendall(_atom.data)
		except:
			kiLog('Socket error')
			self.tcp= None


	def close(self):
		tcp= self.tcp
		self.tcp= None
		if tcp:
			tcp.close()

		self.tcpSock.close()



































import sublime, sublime_plugin
from .muxH264AAC import *
from .mp4Recover import *
from .yiListener import *
from .kiTelnet import *
from .kiLog import *


KiYi= [None, None, None, None, None]

'''
YiOn/Off commands are used to test Stryim in Sublime, `coz its lazy to set up running environment.
'''
class YiOnCommand(sublime_plugin.TextCommand):
	

# =todo 94 (app) +2: handle start-stops
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
		kiLog.states(False, False, True, 'YiListener')
		kiLog.states(True, True, True, 'Mp4Recover')

		selfIP= KiTelnet.defaults(address='192.168.42.1')

		if KiYi[0]:
			kiLog.warn('Already')
			return

		

		muxFlash= KiYi[2]= MuxFLV(SinkFile('D:/yi/restore/stryim/sss+.flv'))
		mp4Restore= Mp4Recover(muxFlash.add)
		KiYi[0]= YiListener()
		KiYi[0].start(self.cbConn, self.cbLive)
		KiYi[0].live(mp4Restore.add, self.cbAir)



class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if not KiYi[0]:
			kiLog.warn('Already')
			return

		KiYi[0].stop()
		KiYi[0]= None

		KiYi[2].stop()
