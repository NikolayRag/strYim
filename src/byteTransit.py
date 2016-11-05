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
	chunk= False

	dispatchCB= None
	trigger= 0
	
	def __init__(self, _dispatchCB, _trigger=0):
		self.dispatchCB= _dispatchCB
		self.trigger= _trigger



	def dispatch(self, _force=False):
		dataLeft= self.chunk.data[self.chunk.position:]

		if not len(dataLeft):
			return 0

		if not _force and len(dataLeft)<self.trigger:
			return 0


		dispatched= False

		if callable(self.dispatchCB):
			dispatched= self.dispatchCB(dataLeft, self.chunk.context)

		if (dispatched or 0)>0:
			self.chunk.position+= dispatched

		return dispatched



	'''
	Check last element context, create new if mismatch
	Retrn True is context was changed
	'''
	def context(self, _ctx):
		if self.chunk and self.chunk.context!=_ctx:
			while self.dispatch(True): #old
				None

		if not self.chunk or self.chunk.context!=_ctx:
			self.chunk= byteTransitChunk(_ctx)	#new

			return True


	'''
	current chunk length
	'''
	def len(self):
		return len(self.chunk.data)



	def add(self, _data, _ctx=None):
		if _ctx:
			self.context(_ctx)

		self.chunk.data+= _data

		self.dispatch()


