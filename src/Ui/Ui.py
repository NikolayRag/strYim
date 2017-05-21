from .AppWindow import *
from MediaStream import *
from SourceYi4k import *


#  todo 218 (app, feature) +0: allow reconfiguration
'''
Gui flow.
Stream can be restarted with different settings.
Camera is controlled constantly.
'''
class Ui():
	args= None
	appSource= None
	appStreamer= None

	appWindow= None

	def __init__(self, _args):
		self.args= _args

		#init
		self.appSource= Yi4k()
		self.appStreamer= Streamer()
		print(self.appStreamer)
		self.appStreamer.link(self.appSource)

	#  todo 242 (feature) +0: check destination
		self.appStreamer.start(_args.args['dst'])
		self.appSource.start()

		self.appWindow= AppWindow(None, None, self.uiDstCanged)
		self.appWindow.destination(_args.args['dst'])

		self.appWindow.exec()

		self.appStreamer.stop()
		self.appSource.stop()



	def uiDstCanged(self, _newVal):
		self.args.args['dst']= _newVal
		self.args.save()
