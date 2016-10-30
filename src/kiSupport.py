def getA(_var, _field, _default=False):
	if not isinstance(_var, dict):
		return _default

	if not _field in _var:
		return _default

	return _var[_field]

