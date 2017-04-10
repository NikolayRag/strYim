# =todo 120 (ui) +0: add ui
import appGui
from args import *
from appControl import *
from appStreamer import *

import logging





flowСamStreamer= None
flowСamControl= None
flowGui= None



#  todo 218 (app, feature) +0: allow reconfiguration


'''
App cleanup and exit point.
'''
def stop():
	flowСamStreamer.stop()
	flowСamControl.stop()




#callbacks

'''
Callback fired when camera is connected/disconnected over WiFi(TCP).
In case of very weak sygnal it can be fired 'disconnected', just ensure camera is close to PC.
'''
def cbConn(_mode):
	if _mode:
		logging.info('Connected')
		flowGui and flowGui.camState('Idle')

	if not _mode:
		logging.info('Disconnected')
		flowGui and flowGui.camState('None')

'''
Callback fired when camera starts/stops recording apropriate file.
There's nothing special to do with it, 'cause data is flown through YiAgent.live() callback.
'''
def cbLive(_mode):
	if _mode==1:
		logging.info('Live')
		flowGui and flowGui.camState('Ready')

	if _mode==0:
		logging.info('Live split')

	if _mode==-1:
		logging.info('Dead')
		flowGui and flowGui.camState('Idle')

'''
Callback fired when data flows to recoverer.
'''
def cbAir(_mode):
	if _mode==1:
		logging.info('Air On')
		flowGui and flowGui.camState('Air')

	if _mode==0:
		logging.info('Air Off')
		flowGui and flowGui.camState('Ready')

	if _mode==-1:
		logging.error('Air bad')
		flowGui and flowGui.camState('Error')


def cbDie():
	logging.info('Exiting')




'''
Gui flow.
Stream can be restarted with different settings.
Camera is controlled constantly.
'''
def runGui(_args):
	YiControl.defaults(ip=_args.args['YiIP'])
	YiStreamer.defaults(ip=_args.args['YiIP'])


	#init
	global flowСamControl, flowСamStreamer
	flowСamControl= YiControl()
	flowСamStreamer= YiStreamer(
		  cbConn=cbConn
		, cbLive=cbLive
		, cbAir=cbAir
		, cbDie=cbDie
	)



	def uiDstCanged(_newVal):
		_args.args['dst']= _newVal
		_args.save()

	flowGui= appGui.Gui(None, None, uiDstCanged)
	flowGui.destination(_args.args['dst'])

#  todo 242 (feature) +0: check destination
	flowСamStreamer.start(_args.args['dst'], _args.formats[0]['fps'])

	flowGui.exec()

	stop()




if __name__ == '__main__':
	cArgs= Args(True)

	if cArgs.args:
		runGui(cArgs)
