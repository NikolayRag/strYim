import io

'''
Buffer incoming binary data and dispatch it to callback fn.

ByteTransit(cb, trigger)
	Init with callback and trigger ammount.

	cb(data, forced)
		Dispatch callback.
		Should return ammount of bytes consumed,
		 remaining chunk will be shifted that size.
		Dispatch is forced when context changes.
		 It will be called assuming all data is consumed.

	trigger
		Size of data available for dispatch callback to take place.
		Zero for immediate dispatch.


add(data, ctx)
	Add binary data with ctx context.
	Switching context forces all remaining data to be dispatched
	 implying it is all consumed. 
'''
class ByteTransit():
	dataIO = None
	context= None

	dispatchCB= None
	trigger= 0
	

	def __init__(self, _dispatchCB, _trigger=0):
		self.dispatchCB= callable(_dispatchCB) and _dispatchCB
		self.trigger= _trigger

		self.dataIO = io.BytesIO(b'')



	def add(self, _data, _ctx=None):
		if self.context!=_ctx:
			self.context= _ctx
			self.dispatch(True)
			


		if _data:
			self.dataIO.write(_data)

			self.dispatch()



	#private

	def dispatch(self, _force=False):
		self.dataIO.seek(0)
		dataLeft= self.dataIO.read()


		if not _force:
			if not len(dataLeft) or len(dataLeft)<self.trigger:
				return 0


		dispatched= self.dispatchCB and self.dispatchCB(dataLeft, _force)

		self.shrink(dispatched)



	def shrink(self, _amt):
		if not _amt:
			return

		self.dataIO.seek(_amt)
		data= self.dataIO.read()

		self.dataIO = io.BytesIO(b'')
		self.dataIO.write(data)
