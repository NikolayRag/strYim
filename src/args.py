import argparse


def parse(_gui=False):
	cParser= argparse.ArgumentParser(description= 'Yi 4k lossless streamer.')

	cParser.add_argument('-nonstop', action='store_true', help='Dont exit when camera pauses.')
	cParser.add_argument('dst', type=str, nargs=('?' if _gui else None), help='streaming destination: rtmp://server/path')

	cParser.add_argument('-logverb', type=str, nargs='+', help=argparse.SUPPRESS)
	cParser.add_argument('-logwarn', type=str, nargs='+', help=argparse.SUPPRESS)

	
	try:
		args= cParser.parse_args()
	except:
		return


	return args
