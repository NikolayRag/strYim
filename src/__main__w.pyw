import stryim
from args import *



if __name__ == '__main__':
	cArgs= Args(True)

	if cArgs.args:
		stryim.runGui(cArgs)


