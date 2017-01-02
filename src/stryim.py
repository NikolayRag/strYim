'''
Following steps must be done once prior to running app:
- enable 8081-8089 ports in firewall
- place blank 'console_enable.script' file in the root of camera's SD-card

Connect to camera WiFi for app to work.
'''



#  todo 120 (ui) +0: add ui

import time, os

from yiControl import *
from stryimLive import *
from mp4.muxH264AAC import *
from telnet.kiTelnet import *
from kiLog import *


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
	nonstop= False

	live= None
	control= None


	'''
	App entry point, should be called once.
	'''
	@staticmethod
	def start(_dst=None, _nonstop=False):
		if Stryim.flagRun:
			kiLog.err('Duplicated init')
			return
		Stryim.flagRun= True


		#pass args
		if _dst!=None:
			Stryim.dst= _dst
		Stryim.nonstop= _nonstop


		#init
		Stryim.control= YiControl()
		Stryim.live= StryimLive(
			  cbConn=Stryim.cbConn
			, cbLive=Stryim.cbLive
			, cbAir=Stryim.cbAir
			, cbDie=Stryim.cbDie
		)


#  todo 218 (app, feature) +0: allow reconfiguration
		#apply settings
		KiTelnet.defaults(address=Stryim.YiIP)
		Yi4kAPI.YiAPI.defaults(ip=Stryim.YiIP)

		#Check for ability to run


#  todo 200 (feature, ui) +0: call from UI
		cFormat= Stryim.formats[0]
		kiLog.ok('Setting ' +str(cFormat['yi']))
		if not Stryim.control.start(cFormat['yi']):
			Stryim.cbDie()
			return

		Stryim.live.start(Stryim.dst, cFormat['fps'])

		while Stryim.flagRun:
			try:
				time.sleep(.1)
			except KeyboardInterrupt:
				kiLog.ok('Exit by demand (Ctrl-C)')
				
				Stryim.nonstop= True
				Stryim.stop()
				break
		


	'''
	App cleanup and exit point.
	'''
	@staticmethod
	def stop():
		Stryim.live.stop()
		Stryim.control.stop()

#  todo 219 (app, clean,feature) +0: wait for .live to stop



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
			kiLog.ok('Air On')

		if _mode==0:
			kiLog.ok('Air Off')

			if not Stryim.nonstop:
				Stryim.stop()
		
		if _mode==-1:
			kiLog.err('Air bad')


	@staticmethod
	def cbDie():
		kiLog.ok('Exiting')

		Stryim.flagRun= False
