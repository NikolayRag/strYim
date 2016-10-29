import sublime, sublime_plugin
import threading

from .kiYiListener import *


KiYi= [None]

class YiOnCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if not KiYi[0]:
			KiYi[0]= KiYiListener()
		KiYi[0].run()


class YiOffCommand(sublime_plugin.TextCommand):
	def run(self, _edit):
		if KiYi[0]:
			KiYi.stop()
