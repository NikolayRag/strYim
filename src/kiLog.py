import inspect

from kiSupport import *

class kiLog():
	#statical collection
	contexts= {
		False:{	#all unspecified
			    'verb':[False, 'verb']
			  , 'ok':[True, 'log']
			  , 'warn':[True, 'warning']
			  , 'err':[True, 'error']
		}
	}


	@staticmethod
	def getCtx(_ctx, _create=False):
		cCtx= getA(kiLog.contexts, _ctx)
		if not cCtx:
			defaultCtx= kiLog.contexts[False]
			cCtx= {
				  'verb': [defaultCtx['verb'][0], str(_ctx)+(' ' if _ctx else '')+defaultCtx['verb'][1]]
				, 'ok': [defaultCtx['ok'][0], str(_ctx)+(' ' if _ctx else '')+defaultCtx['ok'][1]]
				, 'warn': [defaultCtx['warn'][0], str(_ctx)+(' ' if _ctx else '')+defaultCtx['warn'][1]]
				, 'err': [defaultCtx['err'][0], str(_ctx)+(' ' if _ctx else '')+defaultCtx['err'][1]]
			}

			if _create:
				kiLog.contexts[_ctx]= cCtx

		return cCtx


	@staticmethod
	def prefixes(_prefix=None, verb=None, ok=None, warn=None, err=None):
		if _prefix==None:
			_prefix= kiLog.caller()
		cCtx= kiLog.getCtx(_prefix, True)

		if verb!=None:
			cCtx['verb'][1]= str(verb)
		if ok!=None:
			cCtx['ok'][1]= str(ok)
		if warn!=None:
			cCtx['warn'][1]= str(warn)
		if err!=None:
			cCtx['err'][1]= str(err)

		return cCtx


	@staticmethod
	def states(_prefix=None, verb=None, ok=None, warn=None, err=None):
		if _prefix==None:
			_prefix= kiLog.caller()
		cCtx= kiLog.getCtx(_prefix, True)

		if verb!=None:
			cCtx['verb'][0]= not not verb
		if ok!=None:
			cCtx['ok'][0]= not not ok
		if warn!=None:
			cCtx['warn'][0]= not not warn
		if err!=None:
			cCtx['err'][0]= not not err

		return cCtx



	@staticmethod
	def verb(_msg):
		kiLog.printOut('verb', kiLog.caller(), _msg)

	@staticmethod
	def ok(_msg):
		kiLog.printOut('ok', kiLog.caller(), _msg)

	@staticmethod
	def warn(_msg):
		kiLog.printOut('warn', kiLog.caller(), _msg)

	@staticmethod
	def err(_msg):
		kiLog.printOut('err', kiLog.caller(), _msg)


	@staticmethod
	def printOut(_lvl, _pfx, _msg):
		cCtx= kiLog.getCtx(_pfx)

		if (
			not getA(cCtx, _lvl)
			or len(cCtx[_lvl])!=2
			or not cCtx[_lvl][0]
		):
			return

		print(cCtx[_lvl][1] +':', _msg)





	'''
	get class name from which caller of caller() is called lol.
	that is level-2 depth point
	'''
	@staticmethod
	def caller():
		stack= inspect.stack()
		callObj= stack[2][0].f_locals

		o= getA(callObj, 'self')
		if o and hasattr(o,'__class__'):
			return o.__class__.__name__

		return getA(callObj, '__qualname__', '')

