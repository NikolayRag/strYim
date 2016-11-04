








class KiMP4Transit():
	q= False

	
	def __init__(self, _triggerCB=None, _triggerLen=0):
		self.q= [[None, b'']]


	'''
	Check last element context, create new if mismatch
	'''
	def context(self, _ctx):
		cEl= self.q[-1]

		if cEl[0]!=_ctx:
			cEl= [_ctx, b'']
			self.q.append(cEl)

		return len(cEl[1])


	def add(self, _data, _ctx=None):
		if _ctx:
			self.context(_ctx)

		self.q[-1][1]+= _data








import sublime, sublime_plugin
import threading

from .kiYiListener import *


KiYi= [None]

'''
YiOn/Off commands are used to test Stryim in Sublime, `coz its lazy to set up running environment.
'''
class YiOnCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if KiYi[0]:
			kiLog.warn('Already')
			return

		buffer= KiMP4Transit()
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

