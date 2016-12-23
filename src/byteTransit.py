import io

'''
Manage context-grouped chunks of byte data.
Data is added to active chunks, splitted by context and then sequentally dispatched to callback function.


ByteTransit(cb, trigger)
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
class ByteTransitChunk():
	context= None
	dataIO = None
	position= 0
	length= 0

	def __init__(self, _context=None):
		self.context= _context
		self.dataIO = io.BytesIO(b'')
		self.position= 0
		self.length= 0

	def len(self):
		return self.length

	
	def add(self, _data):
		self.dataIO.write(_data)
		self.length+= len(_data)


#  todo 62 (speed, bytes) +0: read more quickly maybe
	def read(self, _from=0, _to=-1):
		self.dataIO.seek(_from)
		return self.dataIO.read(_to)




class ByteTransit():
	chunk= False

	dispatchCB= None
	trigger= 0
	
	def __init__(self, _dispatchCB, _trigger=0):
		self.dispatchCB= _dispatchCB
		self.trigger= _trigger



	def add(self, _data, _ctx=None):
		if _ctx:
			self.context(_ctx)

		if _data:
			self.chunk.add(_data)

			self.dispatch()



	#private

	def dispatch(self, _force=False):
		dataLeft= self.chunk.read(self.chunk.position)


		if not _force:
			if not len(dataLeft) or len(dataLeft)<self.trigger:
				return 0


		dispatched= False

		if callable(self.dispatchCB):
			dispatched= self.dispatchCB(dataLeft, _force)

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
				if self.chunk.position>=self.chunk.len(): #that was last, no need to continue
					break

		if not self.chunk or self.chunk.context!=_ctx:
			self.chunk= ByteTransitChunk(_ctx)	#new

			return True

