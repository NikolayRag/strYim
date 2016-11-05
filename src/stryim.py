import sublime, sublime_plugin
import threading


class mp4Restore():
	cContext= None

	def __init__(self):
		None


	'''
	Provide raw mp4 data to parse.
	Return numer of bytes actually consumed.

		data
			byte string mp4 data

		context
			arbitrary identifier of supplied data
	'''
	def parse(self, _data, _ctx):
		if self.cContext!=_ctx:
			None
		print(len(_data), _ctx)
		return min(len(_data), 10000000)








from .byteTransit import *
from .kiYiListener import *
from .kiTelnet import *
from .kiLog import *


KiYi= [None]

'''
YiOn/Off commands are used to test Stryim in Sublime, `coz its lazy to set up running environment.
'''
class YiOnCommand(sublime_plugin.TextCommand):
	def cbConn(self, _mode):
		kiLog.ok('Connected' if _mode else 'Disconnected')
	def cbLive(self, _mode):
		if _mode==1:
			kiLog.ok('Live')
		if _mode==-1:
			kiLog.ok('Dead')
	def cbAir(self, _mode):
		if _mode==1:
			kiLog.warn('Air On')
		if _mode==0:
			kiLog.warn('Air Off')
		if _mode==-1:
			kiLog.err('Air bad')

	def run(self, _edit):
		if KiYi[0]:
			kiLog.warn('Already')
			return

		selfIP= KiTelnet.defaults('192.168.42.1', 'root', '', 8088)

		restoreO= mp4Restore()
		buffer= byteTransit(restoreO.parse, 10000000)
		KiYi[0]= KiYiListener()
		KiYi[0].start(self.cbConn, self.cbLive)
		KiYi[0].live(buffer, self.cbAir)


class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if not KiYi[0]:
			kiLog.warn('Already')
			return

		KiYi[0].stop()
		KiYi[0]= None

