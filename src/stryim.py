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
	def start(_dst):
		Stryim.selfIP= KiTelnet.defaults(address='192.168.42.1')

		if Stryim.yiApp:
			kiLog.warn('App already on')
			return

		Stryim.muxers= [
			MuxFLV(SinkRTMP(_dst), fps=30000/1001, bps=16000)
		]


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
