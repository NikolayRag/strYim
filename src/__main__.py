import argparse, sys

from stryim import *


if __name__ == '__main__':
	cParser= argparse.ArgumentParser(description= 'Yi 4k lossless streamer.', usage='''
	%(prog)s -h|--help
	%(prog)s destination [-nonstop]
Example:
	%(prog)s rtmp://a.rtmp.youtube.com/live2/your-secret-key

-nonstop:
	Dont exit when camera pauses.
 ''')

	cParser.add_argument('-nonstop', metavar='nonstop', type=bool, nargs='?', const=True, help='Dont exit when camera pauses.')
	cParser.add_argument('dst', metavar='destination', type=str, help='streaming destination; file or rtmp://')
	cParser.add_argument('-logverb', metavar='class', type=str, nargs='+', help='Classes to log verb-level.')
	cParser.add_argument('-logok', metavar='class', type=str, nargs='+', help='Classes to log ok-level.')
	
	try:
		args= cParser.parse_args()
	except:
		sys.exit(0)


	Stryim.start(args.dst, args.nonstop)


