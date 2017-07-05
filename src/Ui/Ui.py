from .AppWindow import *
from MediaStream import *
from SourceYi4k import *


# =todo 218 (app, feature, unsure) +0: allow resolutions reconfiguration
# =todo 326 (app, check) +0: 218/ inspect header passing when restoring camera/stream
# =todo 325 (app, feature, gui) +0: show state
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


		self.appWindow= AppWindow()
		self.appWindow.setSource(self.playSource)
		self.appWindow.setDest(self.args.args['dst'], self.uiDestination, self.playDest)

		self.appSource.setStateCB(self.sourceStateCB)

		self.appWindow.exec()


		self.appStreamer.kill()
		self.appSource.stop()



	def sourceStateCB(self, _state, _msg):
		self.appWindow.camState({Yi4kIdle:'Idle', Yi4kAir:'Air', Yi4kWarn:'Warn', Yi4kErr:'Error'}[_state], _msg)

		if _state==0 or _state==3:
			self.appWindow.btnPlaySource(False)



	def playSource(self, _state):
		if _state:
			self.appSource.start(flat=self.args.args['flat'])
		else:
			self.appSource.stop()



	def playDest(self, _state):
		if _state:
			self.appStreamer.begin(self.args.args['dst'])
		else:
			self.appStreamer.end()



	def uiDestination(self, _newVal):
		self.args.args['dst']= _newVal
		self.args.save()
