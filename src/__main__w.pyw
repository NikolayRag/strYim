import stryim
import args



if __name__ == '__main__':
	cArgs= args.CmdLine(True)

	if cArgs.args:
		stryim.runGui(cArgs)


