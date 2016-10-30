import inspect

from .kiSupport import *

class kiLog():
	#statical collection
	contexts= {
		'':{
			    'ok':[True, 'Log']
			  , 'warn':[True, 'Warning']
			  , 'err':[True, 'Error']
		}
	}


	@staticmethod
	def getCtx(_ctx, _create=False):
		cCtx= getA(kiLog.contexts, _ctx)
		if not cCtx:
			cCtx= {
				  'ok': kiLog.contexts['']['ok'].copy()
				, 'warn': kiLog.contexts['']['warn'].copy()
				, 'err': kiLog.contexts['']['err'].copy()
			}

			if _create:
				kiLog.contexts[_ctx]= cCtx

		return cCtx


	@staticmethod
	def prefixes(_pfxOk=None, _pfxWarn=None, _pfxErr=None, _prefix=False):
		if not _prefix:
			_prefix= kiLog.caller()
		cCtx= kiLog.getCtx(_prefix, True)

		if _pfxOk!=None:
			cCtx['ok'][1]= str(_pfxOk)
		if _pfxWarn!=None:
			cCtx['warn'][1]= str(_pfxWarn)
		if _pfxErr!=None:
			cCtx['err'][1]= str(_pfxErr)

		return cCtx


	@staticmethod
	def states(_stateOk=None, _stateWarn=None, _stateErr=None, _prefix=False):
		if not _prefix:
			_prefix= kiLog.caller()
		cCtx= kiLog.getCtx(_prefix, True)

		if _stateOk!=None:
			cCtx['ok'][0]= not not _stateOk
		if _stateWarn!=None:
			cCtx['warn'][0]= not not _stateWarn
		if _stateErr!=None:
			cCtx['err'][0]= not not _stateErr

		return cCtx



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

		print(cCtx[_lvl][1], _msg)





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

