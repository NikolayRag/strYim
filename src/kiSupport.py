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
