'''
Following steps must be done once prior to running app:
- enable 8081-8089 ports in firewall
- place blank 'console_enable.script' file in the root of camera's SD-card

Connect to camera WiFi for app to work.
'''



# =todo 120 (ui) +0: add ui
# -todo 232 (Yi) +0: add video formats
import time, os

from yiControl import *
from yiStreamer import *
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

formats= [
	{
		'fps':30000./1001,
		'yi':'1920x1080 30P 16:9'
	}
]


flagRun= True

YiIP= '192.168.42.1'
destination= ''
nonstop= False

camStreamer= None
camControl= None


'''
App entry point, should be called once.
'''
def start(_gui=True, _dst=None, _nonstop=False):
	#pass args
	if _dst!=None:
		destination= _dst
	nonstop= _nonstop


	#init
	camControl= YiControl()
	camStreamer= YiStreamer(
		  cbConn=cbConn
		, cbLive=cbLive
		, cbAir=cbAir
		, cbDie=cbDie
	)


#  todo 218 (app, feature) +0: allow reconfiguration
	#apply settings
	KiTelnet.defaults(address=YiIP)
	Yi4kAPI.YiAPI.defaults(ip=YiIP)

	#Check for ability to run


#  todo 200 (feature, ui) +0: call from UI
	cFormat= formats[0]
	kiLog.ok('Setting ' +str(cFormat['yi']))
	if not camControl.start(cFormat['yi']):
		cbDie()
		return

	camStreamer.start(destination, cFormat['fps'])

	while flagRun:
		try:
			time.sleep(.1)
		except KeyboardInterrupt:
			kiLog.ok('Exit by demand (Ctrl-C)')
			
			nonstop= True
			stop()
			break
	


'''
App cleanup and exit point.
'''
def stop():
	camStreamer.stop()
	camControl.stop()




#callbacks

'''
Callback fired when camera is connected/disconnected over WiFi(TCP).
In case of very weak sygnal it can be fired 'disconnected', just ensure camera is close to PC.
'''
def cbConn(_mode):
	kiLog.ok('Connected' if _mode else 'Disconnected')

'''
Callback fired when camera starts/stops recording apropriate file.
There's nothing special to do with it, 'cause data is flown through YiAgent.live() callback.
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
		kiLog.ok('Air On')

	if _mode==0:
		kiLog.ok('Air Off')

		if not nonstop:
			stop()
	
	if _mode==-1:
		kiLog.err('Air bad')


def cbDie():
	kiLog.ok('Exiting')

	flagRun= False
