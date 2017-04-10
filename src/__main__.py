# -todo 238 (app, clean) +1: simplify cmdline flow

import logging

from args import *
from appControl import *
from appStreamer import *

import kiLog



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
		logging.info('Connected')
	if not _mode:
		logging.info('Disconnected')

'''
Callback fired when camera starts/stops recording apropriate file.
There's nothing special to do with it, 'cause data is flown through YiAgent.live() callback.
'''
def cbLive(_mode):
	if _mode==1:
		logging.info('Live')

	if _mode==0:
		logging.info('Live split')

	if _mode==-1:
		logging.info('Dead')

'''
Callback fired when data flows to recoverer.
'''
def cbAir(_mode):
	if _mode==1:
		logging.info('Air On')

	if _mode==0:
		logging.info('Air Off')
		if not cArgs.args['nonstop']:
			stop()
	
	if _mode==-1:
		logging.error('Air bad')


def cbDie():
	logging.info('Exiting')

	global flagRun
	flagRun= False





'''
Commandline flow.
Streaming is done once using some settings,
till interrupted or camera stops (if not -nonstop).
'''
def runCmdline(_args):
	YiControl.defaults(ip=_args.args['YiIP'])
	YiStreamer.defaults(ip=_args.args['YiIP'])


	#init
	flowCamControl= YiControl()
	flowCamStreamer= YiStreamer(
		  cbConn=cbConn
		, cbLive=cbLive
		, cbAir=cbAir
		, cbDie=cbDie
	)

	#Check for ability to run



	cFormat= _args.formats[0]
	logging.info('Setting ' +str(cFormat['yi']))
	if not flowCamControl.start(cFormat['yi']):
		cbDie()
		return

	flowCamStreamer.start(_args.args['dst'], cFormat['fps'])

	while flagRun:
		try:
			time.sleep(.1)
		except KeyboardInterrupt:
			logging.info('Exit by demand (Ctrl-C)')
			
			_args.args['nonstop']= True
			stop()
			break



if __name__ == '__main__':
	cArgs= Args(False)

	if cArgs.args:
		kiLog.state(False, kiLog.ERROR)
		kiLog.state('', kiLog.INFO)

		for c in (cArgs.args['logverb'] or []):
			kiLog.state(c, kiLog.DEBUG)
		for c in (cArgs.args['logwarn'] or []):
			kiLog.state(c, kiLog.WARING)

		runCmdline(cArgs)

