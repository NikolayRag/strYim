from mp4.muxSink import *
from mp4.muxH264AAC import *
from recover.mp4Recover import *
from yiListener import *
from telnet.kiTelnet import *
from kiLog import *


'''
Live control class.
'''
class YiStreamer():
	listener= None
	muxers= []	

	cbConn= None
	cbLive= None
	cbAir= None
	cbDie= None

	def __init__(self, cbConn=None, cbLive=None, cbAir=None, cbDie=None):
		self.cbConn= cbConn
		self.cbLive= cbLive
		self.cbAir= cbAir
		self.cbDie= cbDie




	def setDest(self, _dst, _fps):
		_dst= '/'.join(_dst.split('\\'))
		protocol= _dst.split(':/')
		ext= _dst.split('.')


		MuxFLV.defaults(fps=_fps, srate=48000)
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


		



	def start(self, _dst, fps=30000./1001):
		if self.listener:
			kiLog.warn('Listener already on')
			return

		self.setDest(_dst, fps)

		def muxRelay(data):
			for cMux in self.muxers:
				cMux.add(data)
		mp4Restore= Mp4Recover(muxRelay)


		def listenerDie():
			for cMux in self.muxers:
				cMux.stop()

			callable(self.cbDie) and self.cbDie()


		self.listener= YiListener()
		self.listener.start(self.cbConn, self.cbLive, listenerDie)
		self.listener.live(mp4Restore.add, self.cbAir)



	def stop(self):
		if not self.listener:
			kiLog.warn('Listener already off')
			return

		#additional protect from loop
		listener= self.listener
		self.listener= None
		listener.stop()
