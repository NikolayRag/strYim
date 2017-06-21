import io

'''
Manage context-grouped chunks of byte data.
Data is added to active chunks, splitted by context and then
 sequentally dispatched to callback function.


ByteTransit(cb, trigger)
	Caches added data and dispatch it, respecting consumed ammount. 


	cb(data, forced)
		Dispatch callback.
		Should return ammount of bytes consumed,
		 remaining chunk will be shifted that size.
		Dispatch is forced when context changes. It will be called in a cycle
		 while remaining context is not dried up.

		
	trigger
		Size of data available in chunk for dispatch callback to take place.
		Zero for immediate dispatch.


add(data, ctx)
	Add binary data to ctx context.
	Switching context forces remaining all data to be dispatched
	 implying it is all consumed. 



'''
class ByteTransitChunk():
	dataIO = None
	position= 0
	length= 0

	def __init__(self, _context=None):
		self.dataIO = io.BytesIO(b'')
		self.position= 0
		self.length= 0


	def len(self):
		return self.length-self.position

	
	def add(self, _data):
		self.dataIO.write(_data)
		self.length+= len(_data)


	def read(self, _to=-1):
		self.dataIO.seek(self.position)
		return self.dataIO.read(_to)

	def shrink(self, _amt):
		self.position+= amt




class ByteTransit():
	chunk= False
	context= None

	dispatchCB= None
	trigger= 0
	

	def __init__(self, _dispatchCB, _trigger=0):
		self.dispatchCB= _dispatchCB
		self.trigger= _trigger

		self.chunk= ByteTransitChunk()



	def add(self, _data, _ctx=None):
		if self.context!=_ctx:
			self.flush(_ctx)


		if _data:
			self.chunk.add(_data)

			self.dispatch()



	#private

	def dispatch(self, _force=False):
		dataLeft= self.chunk.read()


		if not _force:
			if not len(dataLeft) or len(dataLeft)<self.trigger:
				return 0


		dispatched= False

		if callable(self.dispatchCB):
			dispatched= self.dispatchCB(dataLeft, _force)

		if (dispatched or 0)>0:
			self.chunk.shrink(dispatched)

		return dispatched



	'''
	Dispatch current chunk
	and recreate new blank
	'''
	def flush(self, _ctx):
		while self.dispatch(True): #old
			if not self.chunk.len(): #that was last, no need to continue
				break

# =todo 315 (bytes, clean) +0: make rolling shrink
		self.chunk= ByteTransitChunk()	#new

