import stryim
import args
from kiLog import *



if __name__ == '__main__':
	cArgs= args.parse()

	if cArgs:
		kiLog.states(False, ok=False, warn=False)
		kiLog.states('', ok=True)

		for c in (cArgs.logverb or []):
			kiLog.states(c, verb=True)
		for c in (cArgs.logwarn or []):
			kiLog.states(c, warn=True)


		stryim.runCmd(cArgs)


