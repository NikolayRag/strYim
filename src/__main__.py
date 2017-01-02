import argparse, sys

import stryim
from kiLog import *


if __name__ == '__main__':
	cParser= argparse.ArgumentParser(description= 'Yi 4k lossless streamer.', usage='''
	%(prog)s -h|--help
	%(prog)s destination [-nonstop]
Example:
	%(prog)s rtmp://a.rtmp.youtube.com/live2/your-secret-key

-nonstop:
	Dont exit when camera pauses.
 ''')

	cParser.add_argument('-nonstop', action='store_true', help='Dont exit when camera pauses.')
	cParser.add_argument('-logverb', type=str, nargs='+', help='Classes to log verb-level.')
	cParser.add_argument('-logwarn', type=str, nargs='+', help='Classes to log warn-level.')
	cParser.add_argument('dst', type=str, help='streaming destination; file or rtmp://')
	
	try:
		args= cParser.parse_args()
	except:
		sys.exit(0)


	kiLog.states(False, ok=False, warn=False)
	kiLog.states('', ok=True)

	for c in (args.logverb or []):
		kiLog.states(c, verb=True)
	for c in (args.logwarn or []):
		kiLog.states(c, warn=True)


	stryim.start(args.dst, args.nonstop)


