'''
Modify logging output by adding class name
'''
import logging, inspect


DEBUG= logging.DEBUG
INFO= logging.INFO
WARNING= logging.WARNING
ERROR= logging.ERROR
CRITICAL= logging.CRITICAL


namesAllowed= {False:ERROR}

def hook(_name, _level, _fn, _ln, _msg, _args, _exInfo, _func, _stack):
	stack= inspect.stack()
	callObj= stack[5][0].f_locals #skip stack to first 'outer' level
	_name= (
		('self' in callObj)
	 	and hasattr(callObj['self'],'__class__')
	 	and callObj['self'].__class__.__name__
	 	or ''
 	)


	testName= _name
	if testName not in namesAllowed:
		testName= False

	if namesAllowed[testName]==None or _level < namesAllowed[testName]:
		_level= -1 #skip record


	return logging.LogRecord(_name, _level, _fn, _ln, _msg, _args, _exInfo)

logging.setLogRecordFactory(hook)



def state(_name, _state=None):
	if _name==False:
		namesAllowed.clear()

	namesAllowed[_name]= _state

	

logging.basicConfig(level= DEBUG, format= '%(name)s %(levelname)s: %(message)s')

