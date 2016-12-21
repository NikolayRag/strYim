from .muxSink import *
from .muxH264AAC import *
from .mp4Recover import *
from .yiListener import *
from .kiTelnet import *
from .kiLog import *


'''
Live control class.
'''
class StryimLive():
	listener= None
	muxers= []	


	'''
	Callback called when camera is connected/disconnected over WiFi(TCP).
	In case of very week sygnal it can be fired 'disconnected', 
	'''
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

	def cbDie(self):
		for cMux in self.muxers:
			cMux.stop()

		kiLog.ok('Exiting')



	def setDest(self, _dst):
		_dst= '/'.join(_dst.split('\\'))
		protocol= _dst.split(':/')
		ext= _dst.split('.')


		muxer= MuxFLV
		sink= SinkRTMP

		if protocol[0]!='rtmp':
			if len(protocol)>1 and protocol[0]=='tcp':
				sink= SinkTCP
			else:
				sink= SinkFile

			if len(ext)>1 and (ext[-1]=='264' or ext[-1]=='h264'):
				muxer= MuxH264
			if len(ext)>1 and ext[-1]=='aac':
				muxer= MuxAAC

		self.muxers=[ muxer(sink(_dst)) ]


		



	def start(self, _dst):
		MuxFLV.defaults(fps=30000./1001, bps=48000./1024)
		self.selfIP= KiTelnet.defaults(address='192.168.42.1')

		if self.listener:
			kiLog.warn('App already on')
			return

		self.setDest(_dst)

		def muxRelay(data):
			for cMux in self.muxers:
				cMux.add(data)
		mp4Restore= Mp4Recover(muxRelay)


		self.listener= YiListener()
		self.listener.start(self.cbConn, self.cbLive, self.cbDie)
		self.listener.live(mp4Restore.add, self.cbAir)



	def stop(self):
		if not self.listener:
			kiLog.warn('App already off')
			return

		self.listener.stop()
		self.listener= None
