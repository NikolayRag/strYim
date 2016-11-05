







'''
Manage context-grouped chunks of byte data.
Data can be added to active chunk, splitted by context;
Incoming data is sequentally sent to provided callback.


byteTransit(cb, trigger)
	Constructor.

	cb(ctx, data)
		Dispatch callback at adding data.
		Should return ammount of bytes consumed - remaining chunk will be shifted that size.
		Data dispatched is always belongs to one context.
		If new context is declared, previous context data will be dispatched until dried out.

			ctx
				current context
			
			data
				all data available
		
	trigger
		Size of data available in chunk for dispatch callback to take place.
		Zero for immediate dispatch.

context(ctx)
	set current chunk to [ctx] context if not yet.


'''
class byteTransit():
	class bChunk():
		context= None
		data= b''
		position= 0


	chunksA= False

	triggerCB= None

	
	def __init__(self, _triggerCB=None, _triggerLen=0):
		self.chunksA= [bChunk()] #blank

		self.triggerCB= _triggerCB


	'''
	Check last element context, create new if mismatch
	'''
	def context(self, _ctx):
		cEl= self.chunksA[-1]

		if cEl[0]!=_ctx:
			cEl= [_ctx, b'']
			self.chunksA.append(cEl)

		return len(cEl[1])


	def add(self, _data, _ctx=None):
		if _ctx:
			self.context(_ctx)

		self.chunksA[-1][1]+= _data








import sublime, sublime_plugin
import threading

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

		kiLog.states(
		      False
		    , False
		    , False
		    , 'KiTelnet'
		)

		KiTelnet.defaults('192.168.42.1', 'root', '', 8088)

		buffer= byteTransit()
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

