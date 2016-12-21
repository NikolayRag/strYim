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
	flagRun= False

	dst= ''

	live= None
	selfIP= None


	'''
	App entry point, should be called once.
	'''
	@staticmethod
	def start(_dst=None):
		if Stryim.flagRun:
			kiLog.err('Duplicated init')
			return
		Stryim.flagRun= True


		kiLog.states(verb=True, ok=True)
		kiLog.states('', verb=True, ok=True)
		kiLog.states('Mp4Recover', verb=True, ok=True)
#		kiLog.states('MuxFLV', warn=False)

		#Yi4k camera constants
		MuxFLV.defaults(srate=48000)
		Stryim.selfIP= KiTelnet.defaults(address='192.168.42.1')


#  todo 200 (feature, ui) +0: call from UI
		if _dst!=None:
			Stryim.dst= _dst


		Stryim.live= StryimLive(
			  cbConn=Stryim.cbConn
			, cbLive=Stryim.cbLive
			, cbAir=Stryim.cbAir
			, cbDie=Stryim.cbDie
		)

		Stryim.live.start(Stryim.dst, 30000./1001)



	'''
	App cleanup and exit point.
	'''
	@staticmethod
	def stop():
		Stryim.live.stop()




	#callbacks

	'''
	Callback fired when camera is connected/disconnected over WiFi(TCP).
	In case of very weak sygnal it can be fired 'disconnected', just ensure camera is close to PC.
	'''
	@staticmethod
	def cbConn(_mode):
		kiLog.ok('Connected' if _mode else 'Disconnected')

	'''
	Callback fired when camera starts/stops recording apropriate file.
	There's nothing special to do with it, 'cause data is flown through YiListener.live() callback.
	'''
	@staticmethod
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
		kiLog.ok('Exiting')

		Stryim.flagRun= False

