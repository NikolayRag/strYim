# -todo 238 (app, clean) +1: simplify cmdline flow

import logging
import kiLog
kiLog.state('', kiLog.INFO)


from args import *
from MediaStream import *
from SourceYi4k import *


appSource= None
appStreamer= None





'''
Commandline flow.
Streaming is done once using some settings,
till interrupted or camera stops (if not -nonstop).
'''
def runCmdline(_args):
	#Check for ability to run
#	cFormat= _args.formats[0]
#	logging.info('Setting ' +str(cFormat['yi']))
#	if not flowCamControl.start(cFormat['yi']):
#		logging.error('Camera error')
#		return


	#init
	appSource= Yi4k()
	appStreamer= Streamer(_args.args['dst'])
	appStreamer.link(appSource)

	appSource.start()


	while not appSource.isIdle():
		try:
			time.sleep(.1)
		except KeyboardInterrupt:
			logging.info('Terminated')
			
#			_args.args['nonstop']= True
			appSource.stop()
			break


	appStreamer.close()




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

