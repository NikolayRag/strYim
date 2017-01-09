from args import *
from appControl import *
from appStreamer import *

from kiLog import *




'''
Yi4k stream app.
Links three flows:
1. Camera live streaming
2. Camera control
3. UI
'''

flowCamStreamer= None
flowCamControl= None

flagRun= True



'''
App cleanup and exit point.
'''
def stop():
	flowCamStreamer.stop()
	flowCamControl.stop()




#callbacks

'''
Callback fired when camera is connected/disconnected over WiFi(TCP).
In case of very weak sygnal it can be fired 'disconnected', just ensure camera is close to PC.
'''
def cbConn(_mode):
	if _mode:
		kiLog.ok('Connected')
	if not _mode:
		kiLog.ok('Disconnected')

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
		if not cArgs.args['nonstop']:
			stop()
	
	if _mode==-1:
		kiLog.err('Air bad')


def cbDie():
	kiLog.ok('Exiting')

	global flagRun
	flagRun= False





'''
Commandline flow.
Streaming is done once using some settings,
till interrupted or camera stops (if not -nonstop).
'''
if __name__ == '__main__':
	cArgs= Args(False)

	if cArgs.args:
		kiLog.states(False, ok=False, warn=False)
		kiLog.states('', ok=True)

		for c in (cArgs.args['logverb'] or []):
			kiLog.states(c, verb=True)
		for c in (cArgs.args['logwarn'] or []):
			kiLog.states(c, warn=True)



		YiControl.defaults(ip=cArgs.args['YiIP'])
		YiStreamer.defaults(ip=cArgs.args['YiIP'])


		#init
		flowCamControl= YiControl()
		flowCamStreamer= YiStreamer(
			  cbConn=cbConn
			, cbLive=cbLive
			, cbAir=cbAir
			, cbDie=cbDie
		)

		#Check for ability to run



		cFormat= cArgs.formats[0]
		kiLog.ok('Setting ' +str(cFormat['yi']))
		if not flowCamControl.start(cFormat['yi']):
			cbDie()
		else:
			flowCamStreamer.start(cArgs.args['dst'], cFormat['fps'])

			while flagRun:
				try:
					time.sleep(.1)
				except KeyboardInterrupt:
					kiLog.ok('Exit by demand (Ctrl-C)')
					
					cArgs.args['nonstop']= True
					stop()
					break
