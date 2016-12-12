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
