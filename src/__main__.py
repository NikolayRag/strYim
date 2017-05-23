import logging, kiLog

from args import *
from MediaStream import *
from SourceYi4k import *

import threading


'''
Streaming is done once till interrupted or camera stops.
'''
if __name__ == '__main__':
	cArgs= Args(False)

	if cArgs.args:
		kiLog.state(False)
		kiLog.state('', kiLog.INFO)
		kiLog.state('Streamer', kiLog.INFO)
		kiLog.state('Yi4k', kiLog.INFO)
		
		for c in (cArgs.args['logverb'] or []):
			kiLog.state(c, kiLog.DEBUG)
		for c in (cArgs.args['logwarn'] or []):
			kiLog.state(c, kiLog.WARING)


		#init
		appSource= Yi4k()
		appStreamer= Streamer()
		appStreamer.link(appSource)

		appStreamer.begin(cArgs.args['dst'])
		appSource.start()


		#handle ctrl-c
		while not appSource.isIdle():
			try:
				time.sleep(.1)
			except KeyboardInterrupt:
				logging.info('Terminated')
				break

		#finish
		threading.Timer(0,appSource.stop).start()
		threading.Timer(0,lambda:appStreamer.end(True)).start()


		#prevent breaking shutdows routines by ctrl-c
		while len(threading.enumerate())>1:
			try:
				time.sleep(.5)
			except KeyboardInterrupt:
				logging.warning('Cooldown in progress')
