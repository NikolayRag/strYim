import argparse, sys

from stryim import *
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

	cParser.add_argument('-nonstop', type=bool, nargs='?', const=True, help='Dont exit when camera pauses.')
	cParser.add_argument('-logverb', type=str, nargs='+', help='Classes to log verb-level.')
	cParser.add_argument('-logok', type=str, nargs='+', help='Classes to log ok-level.')
	cParser.add_argument('dst', type=str, help='streaming destination; file or rtmp://')
	
	try:
		args= cParser.parse_args()
	except:
		sys.exit(0)

	if args.logok:
		for c in args.logok:
			kiLog.states(c, ok=True)
	if args.logverb:
		for c in args.logverb:
			kiLog.states(c, ok=True, verb=True)


	Stryim.start(args.dst, args.nonstop)


