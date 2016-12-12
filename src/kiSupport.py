def getA(_var, _field, _default=False):
	if not isinstance(_var, dict):
		return _default

	if not _field in _var:
		return _default

	return _var[_field]


def pad(_val, _pad=4):
	_val= str(_val)
	valLen= min(len(_val),_pad)

	return '0'*(_pad-valLen) +_val[-valLen:]

def bitsCollect(_bitPairs, _int=False):
	rlen= 0
	result= 0
	for cLen,cVal in _bitPairs:
		result= (result<<cLen) +cVal
		rlen+= cLen

	if _int:
		return result

	return result.to_bytes(int(rlen/8)+(rlen%8>0), 'big')

#  todo 140 (optimize) +0: OPTIMIZE
def bitsGet(_data, _len, _pos):
	startByte= _pos[0]
	startBit= _pos[1]
	endBit= (startByte<<3) +startBit +_len
	endByte= (endBit>>3) +(endBit%8>0)
	endBit-= (endByte-1)<<3

	d= _data[startByte:endByte]
	if len(d) < endByte-startByte:	#underflow
		d+= b'\x00'*(endByte-startByte-len(d))

	res= int.from_bytes(d,'big')
	res&= (1<<(endByte-startByte)*8-startBit)-1
	res>>= 8-endBit

	_pos[0]= endByte-1
	_pos[1]= endBit

	return res


