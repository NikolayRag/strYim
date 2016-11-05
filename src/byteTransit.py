'''
Manage context-grouped chunks of byte data.
Data is added to active chunks, splitted by context and then sequentally dispatched to callback function.


byteTransit(cb, trigger)
	Constructor.

	cb(data, ctx)
		Dispatch callback at adding data.
		Should return ammount of bytes consumed - remaining chunk will be shifted that size.
		Data dispatched is always belongs to one context.
		If new context is declared, previous context data will be dispatched in cycle until dried out.
		In that case callback returning 0 or False is assumed as all data been consumed, and cycle will end.

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
class byteTransitChunk():
	context= None
	data= b''
	position= 0

	def __init__(self, _context=None):
		self.context= _context
		self.data= b''
		self.position= 0


class byteTransit():
	chunksA= False

	dispatchCB= None
	trigger= 0
	
	def __init__(self, _dispatchCB, _trigger=0):
		self.chunksA= [byteTransitChunk()] #blank

		self.dispatchCB= _dispatchCB
		self.trigger= _trigger



#  todo 37 (transit, clean) +0: remove dried context more precisely
	def dispatch(self, _cEl, _force=False):
		dataToSend= _cEl.data[_cEl.position:]

		if not len(dataToSend):
			return 0

		if not _force and len(dataToSend)<self.trigger:
			return 0


		dispatched= False

		if callable(self.dispatchCB):
			dispatched= self.dispatchCB(dataToSend, _cEl.context)

		if (dispatched or 0)>0:
			_cEl.position+= dispatched

		return dispatched



	'''
	Check last element context, create new if mismatch
	'''
	def context(self, _ctx):
		cEl= self.chunksA[-1]

		if cEl.context!=_ctx:
			while self.dispatch(cEl, True): #old
				None

			self.chunksA= self.chunksA[1:] #shift


			cEl= byteTransitChunk(_ctx)	#new
			self.chunksA.append(cEl)


		return len(cEl.data)



	def add(self, _data, _ctx=None):
		if _ctx:
			self.context(_ctx)

		cEl= self.chunksA[-1]
		cEl.data+= _data

		self.dispatch(cEl)








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

		def pp(data, ctx):
			print(len(data), ctx)
			return len(data)

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

