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
		self.appStreamer.link(self.appSource)


		self.appWindow= AppWindow(self.start, self.stop)
		self.appWindow.destination(self.args.args['dst'], changedCB=self.uiDestination)

		self.appWindow.exec()



	def start(self, _dst):
		self.appStreamer.start(_dst)
		self.appSource.start()


	
	def stop(self):
		self.appStreamer.kill()
		self.appSource.stop()



	def uiDestination(self, _newVal):
		self.args.args['dst']= _newVal
		self.args.save()
