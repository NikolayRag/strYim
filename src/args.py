import argparse, os



class CmdLine():
	args= None
	
	def __init__(self, _reuseOld=True):
		self.formArgs(not _reuseOld)

		

	def save(self):
		None



	def formArgs(self, _forceDst):
		cParser= argparse.ArgumentParser(description= 'Yi 4k lossless streamer.')

		cParser.add_argument('-nonstop', action='store_true', help='Dont exit when camera pauses.')
		cParser.add_argument('dst', type=str, nargs=(None if _forceDst else '?'), help='streaming destination: rtmp://server/path')

		cParser.add_argument('-logverb', type=str, nargs='+', help=argparse.SUPPRESS)
		cParser.add_argument('-logwarn', type=str, nargs='+', help=argparse.SUPPRESS)

		
		try:
			self.args= vars(cParser.parse_args())

			return True
		
		except:
			self.args= False

			return False


