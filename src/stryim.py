import sublime, sublime_plugin
import threading

from .byteTransit import *
from .kiYiListener import *
from .kiTelnet import *
from .kiLog import *


KiYi= [None]

'''
YiOn/Off commands are used to test Stryim in Sublime, `coz its lazy to set up running environment.
'''
class YiOnCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if KiYi[0]:
			kiLog.warn('Already')
			return

		KiTelnet.defaults('192.168.42.1', 'root', '', 8088)

		def pp(data, ctx):
			print(len(data), ctx)
			return min(len(data), 10000000)

		buffer= byteTransit(pp, 10000000)
		KiYi[0]= KiYiListener(buffer)
		KiYi[0].start()
		KiYi[0].live()


class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if not KiYi[0]:
			kiLog.warn('Already')
			return

		KiYi[0].stop()
		KiYi[0]= None

