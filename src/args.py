import argparse


def parse(_gui=False):
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
	cParser.add_argument('dst', type=str, nargs=('?' if _gui else None), help='streaming destination; rtmp://server/path')
	
	try:
		args= cParser.parse_args()
	except:
		return


	return args
