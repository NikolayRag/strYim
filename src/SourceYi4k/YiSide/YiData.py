'''
Construct/restore network chunk for transfer from Yi.
'''
class YiData():
	import json
	global json


	meta= b''
	binary= b''

	restoreCB= None



	@staticmethod
	def build(_binary, _ctx):
		return json.dumps({'ctx':_ctx, 'len':len(_binary)})



	def __init__(self, _cb=None):
		self.restoreCB= _cb



	def restore(self, _data):
		if _data:
			if callable(self.restoreCB):
				self.restoreCB(_data)
