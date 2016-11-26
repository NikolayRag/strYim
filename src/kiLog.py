import inspect

from .kiSupport import *

class kiLog():
	#statical collection
	contexts= {
		'':{
			    'verb':[False, 'verb']
			    'ok':[False, 'log']
			  , 'warn':[True, 'warning']
			  , 'err':[True, 'error']
		}
	}


	@staticmethod
	def getCtx(_ctx, _create=False):
		cCtx= getA(kiLog.contexts, _ctx)
		if not cCtx:
			defaultCtx= kiLog.contexts['']
			cCtx= {
				  'verb': [defaultCtx['verb'][0], str(_ctx)+' '+defaultCtx['verb'][1]]
				, 'ok': [defaultCtx['ok'][0], str(_ctx)+' '+defaultCtx['ok'][1]]
				, 'warn': [defaultCtx['warn'][0], str(_ctx)+' '+defaultCtx['warn'][1]]
				, 'err': [defaultCtx['err'][0], str(_ctx)+' '+defaultCtx['err'][1]]
			}

			if _create:
				kiLog.contexts[_ctx]= cCtx

		return cCtx


	@staticmethod
	def prefixes(_pfxVerb=None, _pfxOk=None, _pfxWarn=None, _pfxErr=None, _prefix=False):
		if not _prefix:
			_prefix= kiLog.caller()
		cCtx= kiLog.getCtx(_prefix, True)

		if _pfxVerb!=None:
			cCtx['verb'][1]= str(_pfxVerb)
		if _pfxOk!=None:
			cCtx['ok'][1]= str(_pfxOk)
		if _pfxWarn!=None:
			cCtx['warn'][1]= str(_pfxWarn)
		if _pfxErr!=None:
			cCtx['err'][1]= str(_pfxErr)

		return cCtx


	@staticmethod
	def states(_stateVerb=None, _stateOk=None, _stateWarn=None, _stateErr=None, _prefix=False):
		if not _prefix:
			_prefix= kiLog.caller()
		cCtx= kiLog.getCtx(_prefix, True)

		if _stateVerb!=None:
			cCtx['verb'][0]= not not _stateVerb
		if _stateOk!=None:
			cCtx['ok'][0]= not not _stateOk
		if _stateWarn!=None:
			cCtx['warn'][0]= not not _stateWarn
		if _stateErr!=None:
			cCtx['err'][0]= not not _stateErr

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

