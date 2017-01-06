'''
Following steps must be done once prior to running app:
- enable 8081-8089 ports in firewall
- place blank 'console_enable.script' file in the root of camera's SD-card

Connect to camera WiFi for app to work.
'''



# =todo 120 (ui) +0: add ui
# -todo 232 (Yi) +0: add video formats
import time, os

from appControl import *
from appStreamer import *

from kiLog import *


class Object():
	None


'''
Yi4k stream app.
Links three flows:
1. Camera live streaming
2. Camera control
3. UI
'''

pool= Object()
pool.formats= [
	{
		'fps':30000./1001,
		'yi':'1920x1080 30P 16:9'
	}
]

state= Object()
state.flagRun= True

config= Object()
config.YiIP= '192.168.42.1'
config.destination= ''
config.nonstop= False

flow= Object()
flow.camStreamer= None
flow.camControl= None
flow.gui= None


def init(_dst=None, _nonstop=False):
	#pass args
	if _dst!=None:
		config.destination= _dst
	config.nonstop= _nonstop


	YiControl.defaults(ip=config.YiIP)
	YiStreamer.defaults(ip=config.YiIP)


	#init
	flow.camControl= YiControl()
	flow.camStreamer= YiStreamer(
		  cbConn=cbConn
		, cbLive=cbLive
		, cbAir=cbAir
		, cbDie=cbDie
	)



'''
App entry points, should be called once.
'''


'''
Gui flow.
Stream can be restarted with different settings.
Camera is controlled constantly.
'''
def runGui(_args):
	#import on demand to allow PyInstaller to exclude it
	import appGui

	init(_args.dst, _args.nonstop)

	flow.gui= appGui.gui()

	flow.gui.exec()

#  todo 218 (app, feature) +0: allow reconfiguration



'''
Commandline flow.
Streaming is done once using some settings,
till interrupted or camera stops.
'''
def runCmd(_args):
	init(_args.dst, _args.nonstop)

	#Check for ability to run


#  todo 200 (feature, ui) +0: call from UI
	cFormat= pool.formats[0]
	kiLog.ok('Setting ' +str(cFormat['yi']))
	if not flow.camControl.start(cFormat['yi']):
		cbDie()
		return

	flow.camStreamer.start(config.destination, cFormat['fps'])

	while state.flagRun:
		try:
			time.sleep(.1)
		except KeyboardInterrupt:
			kiLog.ok('Exit by demand (Ctrl-C)')
			
			config.nonstop= True
			stop()
			break
	


'''
App cleanup and exit point.
'''
def stop():
	flow.camStreamer.stop()
	flow.camControl.stop()




#callbacks

'''
Callback fired when camera is connected/disconnected over WiFi(TCP).
In case of very weak sygnal it can be fired 'disconnected', just ensure camera is close to PC.
'''
def cbConn(_mode):
	if _mode:
		kiLog.ok('Connected')
		flow.gui and flow.gui.camState('Idle')

	if not _mode:
		kiLog.ok('Disconnected')
		flow.gui and flow.gui.camState('None')

'''
Callback fired when camera starts/stops recording apropriate file.
There's nothing special to do with it, 'cause data is flown through YiAgent.live() callback.
'''
def cbLive(_mode):
	if _mode==1:
		kiLog.ok('Live')
		flow.gui and flow.gui.camState('Ready')

	if _mode==0:
		kiLog.ok('Live split')

	if _mode==-1:
		kiLog.ok('Dead')
		flow.gui and flow.gui.camState('Idle')

'''
Callback fired when data flows to recoverer.
'''
def cbAir(_mode):
	if _mode==1:
		kiLog.ok('Air On')
		flow.gui and flow.gui.camState('Air')

	if _mode==0:
		kiLog.ok('Air Off')
		flow.gui and flow.gui.camState('Ready')

		if not config.nonstop:
			stop()
	
	if _mode==-1:
		kiLog.err('Air bad')
		flow.gui and flow.gui.camState('Error')


def cbDie():
	kiLog.ok('Exiting')

	state.flagRun= False
