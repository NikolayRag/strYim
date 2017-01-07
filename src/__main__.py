import stryim
import args
from kiLog import *



if __name__ == '__main__':
	cArgs= args.CmdLine(False)

	if cArgs.args:
		kiLog.states(False, ok=False, warn=False)
		kiLog.states('', ok=True)

		for c in (cArgs.args['logverb'] or []):
			kiLog.states(c, verb=True)
		for c in (cArgs.args['logwarn'] or []):
			kiLog.states(c, warn=True)


		stryim.runCmd(cArgs)


