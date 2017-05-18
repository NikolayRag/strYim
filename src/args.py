import argparse, os, json
import logging


'''
Deal with app settings.
Loads previously saved and put commandline arguments over.
'''
class Args():
	appName='stryim'
	settingsFile= os.path.join(os.path.expanduser('~'), ".%s/%s.ini" % (appName,appName))

	args= None



	'''
	_reuseOld tells to load saved settings.
	If set, 'dst' is not required.
	'''
	def __init__(self, _reuseOld=True):
		cmdArgs= self.parseCmdline(not _reuseOld)
		if not cmdArgs:
			return


		if not _reuseOld:
			self.args= cmdArgs
			return


		self.args= self.load()

		#full init args
		if not self.args:
			self.args= cmdArgs
			return


		#overwrite loaded with cmd
		for cArg in cmdArgs:
			if cmdArgs[cArg]!=None:
				self.args[cArg]= cmdArgs[cArg]



	'''
	Save current settings to application related file.
	'''
	def save(self):
		settings= json.dumps(self.args, sort_keys=True, indent=4)

		try:
			if not os.path.exists(os.path.dirname(self.settingsFile)):
				os.makedirs(os.path.dirname(self.settingsFile))

			f= open(self.settingsFile, 'w')
			f.write(settings)
		except:
			logging.warning('Settings could not be saved.')
			return


		f.close()



	#private

	def load(self):
		try:
			f= open(self.settingsFile, 'r')
		except:
			logging.warning('No stored settings found.')
			return


		try:
			settingsStr= f.read()
		except:
			logging.warning('Setting file couldnt\'t be read')
			return

		f.close()


		try:
			return json.loads(settingsStr)
		except:
			logging.warning('Setting file corrupt')
			return



	def parseCmdline(self, _forceDst):
		cParser= argparse.ArgumentParser(description= 'Yi 4k lossless streamer.')

#		cParser.add_argument('-nonstop', default=False, action='store_true', help='Dont exit when camera pauses.')
		cParser.add_argument('dst', type=str, nargs=(None if _forceDst else '?'), help='streaming destination: rtmp://server/path')

		cParser.add_argument('-YiIP', default='192.168.42.1', type=str, help=argparse.SUPPRESS)
		cParser.add_argument('-logverb', default=False, type=str, nargs='+', help=argparse.SUPPRESS)
		cParser.add_argument('-logwarn', default=False, type=str, nargs='+', help=argparse.SUPPRESS)

		
		try:
			return vars(cParser.parse_args())
		except:
			return False


