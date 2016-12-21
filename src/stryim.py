#  todo 120 (ui) +0: add ui

from .stryimLive import *
from .muxH264AAC import *
from .kiTelnet import *
from .kiLog import *


'''
Yi4k stream app.
Links three flows:
1. Camera live streaming
2. Camera state
3. UI
'''
class Stryim():
	live= None
	selfIP= None


	'''
	App entry point, should be called once.
	'''
	@staticmethod
	def start(_dst):
		KiLog.states('', verb=True, ok=True)
		KiLog.states('Mp4Recover', verb=True, ok=True)
#		KiLog.states('MuxFLV', warn=False)

		#Yi4k camera constants
		MuxFLV.defaults(srate=48000)
		Stryim.selfIP= KiTelnet.defaults(address='192.168.42.1')


#  todo 200 (feature, ui) +0: call from UI
		Stryim.live= StryimLive(
			  cbConn=Stryim.cbConn
			, cbLive=Stryim.cbLive
			, cbAir=Stryim.cbAir
			, cbDie=Stryim.cbDie
		)

		Stryim.live.start('D:/yi/restore/stryim/L.flv', 30000./1001)



	'''
	App cleanup and exit point.
	'''
	@staticmethod
	def stop():
		Stryim.live.stop()






	'''
	Callback fired when camera is connected/disconnected over WiFi(TCP).
	In case of very weak sygnal it can be fired 'disconnected', just ensure camera is close to PC.
	'''
	def cbConn(_mode):
		kiLog.ok('Connected' if _mode else 'Disconnected')

	'''
	Callback fired when camera starts/stops recording apropriate file.
	There's nothing special to do with it, 'cause data is flown through YiListener.live() callback.
	'''
	def cbLive(_mode):
		if _mode==1:
			kiLog.ok('Live')
		if _mode==0:
			kiLog.ok('Live split')
		if _mode==-1:
			kiLog.ok('Dead')
	
	'''
	Callback fired when data flows to recoverer.
	'''
	def cbAir(_mode):
		if _mode==1:
			kiLog.warn('Air On')
		if _mode==0:
			kiLog.warn('Air Off')
		if _mode==-1:
			kiLog.err('Air bad')


	def cbDie(self):
		kiLog.ok('Exiting')
