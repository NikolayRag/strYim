'''
Yi4k camera required to be available at 192.168.42.1 and telnet-enabled
'''

import kiLog

import logging, threading, time

import SourceYi4k, MediaStream



def t1():
	kiLog.state('YiPy', kiLog.INFO)

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


	logging.info('YiPy: %s, %s' % (yiPyResult[0]==b'4\r\n', yiPyResult[0]))




def t2():
	kiLog.state('YiReader', kiLog.INFO)

	resCnt= [0]
	def agentCB(res):
		resCnt[0]+= len(res or b'')

	yi= SourceYi4k.YiReader()
	threading.Timer(0, lambda:yi.yiListen(agentCB)).start()

	wdog= threading.Timer(6, yi.yiClose)
	wdog.start()
	yiReaderRes= yi.yiRunAgent('test')
	wdog.cancel()


	logging.info('YiAgent: %s, total %s bytes' % (yiReaderRes, resCnt[0]))




def t3():
	kiLog.state('YiReader', kiLog.INFO)

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
	kiLog.state('YiControl', kiLog.INFO)

	yiControl= SourceYi4k.YiControl(None)
	yiOk= yiControl.start(30, 1080)

# -todo 278 (Yi, fix) +0: immedeate stop after start fails
	if yiOk:
		time.sleep(5)
		yiOk= yiControl.stop()
	
	logging.info('YiControl: %s' % yiOk)

	time.sleep(6)




def t5():
	kiLog.state('Mp4Recover', kiLog.ERROR)
	kiLog.state('Yi4k', kiLog.INFO)

	stats= {'avc-k':0, 'avc':0, 'aac':0}

	def atomCB(atom):
		if atom.typeAVC:
			if atom.AVCKey:
				stats['avc-k']+= 1
			else:
				stats['avc']+= 1
		if atom.typeAAC:
			stats['aac']+= 1


	yi4k= SourceYi4k.Yi4k(atomCB)
	threading.Timer(10, yi4k.stop).start()
	yiReaderRes= yi4k.start()


	logging.info('Yi4k: %s, %s' % (yiReaderRes, stats))



def t6():
	kiLog.state('Streamer', kiLog.INFO)

	streamer= MediaStream.Streamer('test.flv')
	streamerRes= streamer.close()

	logging.info('Streamer: %s' % streamerRes)




def t7():
	kiLog.state('Streamer', kiLog.INFO)
	kiLog.state('MuxFLV', kiLog.INFO)
	kiLog.state('SinkRTMP', kiLog.INFO)

	yi4k= SourceYi4k.Yi4k()
	streamer= MediaStream.Streamer('tmp.flv')
	streamer.link(yi4k)

	threading.Timer(0, yi4k.start).start()
	threading.Timer(10, yi4k.stop).start()
	threading.Timer(15, streamer.close).start()

	logging.info('App ok')




kiLog.state(False, kiLog.ERROR)
kiLog.state('', kiLog.INFO)
#t1(); print()
kiLog.state(False, kiLog.ERROR)
kiLog.state('', kiLog.INFO)
#t2(); print()
kiLog.state(False, kiLog.ERROR)
kiLog.state('', kiLog.INFO)
#t3(); print()
kiLog.state(False, kiLog.ERROR)
kiLog.state('', kiLog.INFO)
#t4(); print()
kiLog.state(False, kiLog.ERROR)
kiLog.state('', kiLog.INFO)
#t5(); print()
kiLog.state(False, kiLog.ERROR)
kiLog.state('', kiLog.INFO)
#t6(); print()
kiLog.state(False, kiLog.ERROR)
kiLog.state('', kiLog.INFO)
t7(); print()

logging.info('End')
