#  todo 120 (ui) +0: add ui

import sublime, sublime_plugin
from .muxSink import *
from .muxH264AAC import *
from .mp4Recover import *
from .yiListener import *
from .kiTelnet import *
from .kiLog import *


'''
main Yi control class
'''
class Stryim():
	yiApp= None	#instance of yiListener
	muxers= []	


	@staticmethod
	def cbConn(_mode):
		kiLog.ok('Connected' if _mode else 'Disconnected')

	@staticmethod
	def cbLive(_mode):
		if _mode==1:
			kiLog.ok('Live')
		if _mode==-1:
			kiLog.ok('Dead')
	
	@staticmethod
	def cbAir(_mode):
		if _mode==1:
			kiLog.warn('Air On')
		if _mode==0:
			kiLog.warn('Air Off')
		if _mode==-1:
			kiLog.err('Air bad')

	@staticmethod
	def cbDie():
		for cMux in Stryim.muxers:
			cMux.stop()

		kiLog.ok('Exiting')



	@staticmethod
	def setDest(_dst):
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

		Stryim.muxers=[ muxer(sink(_dst)) ]


		



	@staticmethod
	def start(_dst):
		MuxFLV.defaults(fps=30000/1001, bps=16000)
		Stryim.selfIP= KiTelnet.defaults(address='192.168.42.1')

		if Stryim.yiApp:
			kiLog.warn('App already on')
			return

		Stryim.setDest(_dst)

		def muxRelay(data):
			for cMux in Stryim.muxers:
				cMux.add(data)
		mp4Restore= Mp4Recover(muxRelay)


		Stryim.yiApp= YiListener()
		Stryim.yiApp.start(Stryim.cbConn, Stryim.cbLive, Stryim.cbDie)
		Stryim.yiApp.live(mp4Restore.add, Stryim.cbAir)



	@staticmethod
	def stop():
		if not Stryim.yiApp:
			kiLog.warn('App already off')
			return

		Stryim.yiApp.stop()
		Stryim.yiApp= None
