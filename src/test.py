'''
Yi4k camera required to be available at 192.168.42.1 and telnet-enabled
'''


import kiLog
kiLog.state('YiReader', kiLog.DEBUG)
kiLog.state('Yi4k', kiLog.DEBUG)
kiLog.state('', kiLog.INFO)


import logging, threading, time

import SourceYi4k



def t1():
	yipyBlock= threading.Event()
	yiPyResult= [None]
	def yiRes(_res):
		yiPyResult[0]= _res
		logging.debug('Yi Py res: %s' % _res)
		yipyBlock.set()

	yipy= SourceYi4k.YiPy()
	yipy.run('print(2+2)')

	logging.debug('YiPy wait')
	yipy.wait(yiRes)
	yipyBlock.wait()

	if yiPyResult[0]==b'4\r\n':
		logging.info('YiPy ok: %s' % yiPyResult[0])
	else:
		logging.error('YiPy err')




def t2():
	resCnt= [0]
	def agentCB(res):
		resCnt[0]+= len(res or b'')

	yi= SourceYi4k.YiReader()
	threading.Timer(0, lambda:yi.yiListen(agentCB)).start()

	wdog= threading.Timer(6, yi.yiClose)
	wdog.start()
	yiReaderRes= yi.yiRunAgent('test')
	wdog.cancel()


	if yiReaderRes:
		logging.info('YiReader ok, total %s bytes' % resCnt[0])
	else:
		logging.error('YiReader err')




def t3():
	dataLen=[0]

	t1= [time.time()]
	def metaCB(_res):
		if not t1[0]:
			t1[0]= time.time()

		logging.info(_res)

	def dataCB(_res):
		dataLen[0]+= len(_res)


	yi= SourceYi4k.YiReader()
	threading.Timer(10, yi.yiClose).start()
	yiReaderRes= yi.start(dataCB, metaCB)

	logging.info('YiReader: %s, %d rate' % (yiReaderRes, dataLen[0]/(time.time()-t1[0])))




def t4():
	def atomCB(atom):
		aType='?'
		if atom.typeMoov:
			aType= 'MOOV'
		if atom.typeAVC:
			aType= '264'
			if atom.AVCKey:
				aType+= ' key'
			if not atom.AVCVisible:
				aType+= ' invis'
		if atom.typeAAC:
			aType= 'AAC'


		print(aType, atom.outPos-atom.inPos)

	yi4k= SourceYi4k.Yi4k(atomCB)
	threading.Timer(10, yi4k.stop).start()
	yi4k.start()
#	yiReaderRes= yi4k.wait()


#	logging.info('Yi4k: %s' % yiReaderRes)




#t1(); print()
#t2(); print()
#t3(); print()
t4(); print()

logging.info('End')
