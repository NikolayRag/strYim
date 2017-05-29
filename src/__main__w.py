import Ui
from args import *
import kiLog
kiLog.state(False, kiLog.WARNING)
kiLog.state('Yi4k', kiLog.INFO)
kiLog.state('Streamer', kiLog.INFO)


'''
Gui flow.
Stream can be restarted with different settings.
Camera is controlled constantly.
'''
if __name__ == '__main__':
	cArgs= Args(True)

	if cArgs.args:
		Ui.Ui(cArgs)
