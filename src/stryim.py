'''
Following steps must be done once prior to running app:
- enable 8081-8089 ports in firewall
- place blank 'console_enable.script' file in the root of camera's SD-card

Connect to camera WiFi for app to work.
'''



#  todo 120 (ui) +0: add ui

from .yiControl import *

from .stryimLive import *
from .muxH264AAC import *
from .kiTelnet import *
from .kiLog import *


'''
Yi4k stream app.
Links three flows:
1. Camera live streaming
2. Camera control
3. UI
'''
class Stryim():
	formats= [
		{
			'fps':30000./1001,
			'yi':'1920x1080 30P 16:9'
		}
	]


	flagRun= False

	YiIP= '192.168.42.1'
	dst= ''

	live= None
	control= None


	'''
	App entry point, should be called once.
	'''
	@staticmethod
	def start(_dst=None):
		if Stryim.flagRun:
			kiLog.err('Duplicated init')
			return
		Stryim.flagRun= True


#		kiLog.states(verb=True, ok=True)
#		kiLog.states('', verb=True, ok=True)
#		kiLog.states('Mp4Recover', verb=True, ok=True)
#		kiLog.states('MuxFLV', warn=False)

		#Yi4k camera constants
		KiTelnet.defaults(address=Stryim.YiIP)

		if _dst!=None:
			Stryim.dst= _dst


		#Cheak for ability to run



		#init
		Stryim.control= YiControl()
		Stryim.live= StryimLive(
			  cbConn=Stryim.cbConn
			, cbLive=Stryim.cbLive
			, cbAir=Stryim.cbAir
			, cbDie=Stryim.cbDie
		)


		YiAPI.defaults(ip=Stryim.YiIP)
#  todo 200 (feature, ui) +0: call from UI
		formatI= 0
		if Stryim.control.start(Stryim.formats[formatI]['yi']):
			Stryim.live.start(Stryim.dst, Stryim.formats[formatI]['fps'])



	'''
	App cleanup and exit point.
	'''
	@staticmethod
	def stop():
		Stryim.live.stop()
		Stryim.control.stop()




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
