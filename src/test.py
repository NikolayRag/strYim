'''
Yi4k camera required to be available at 192.168.42.1 and telnet-enabled
'''

import kiLog

import logging, threading, time

import SourceYi4k, MediaStream


#runnung simple code at yi side
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



#read synthetic data from yi
def t2():
	kiLog.state('YiReader', kiLog.INFO)

	resCnt= [0]
	def agentCB(res):
		resCnt[0]+= len(res or b'')

	yi= SourceYi4k.YiReader()
	threading.Timer(0, lambda:yi.yiListen(agentCB)).start()

	wdog= threading.Timer(6, yi.stop)
	wdog.start()
	yiReaderRes= yi.yiRunAgent('test')
	wdog.cancel()


	logging.info('YiAgent: %s, total %s bytes' % (yiReaderRes, resCnt[0]))



#read available stream from yi
def t3():
	kiLog.state('YiReader', kiLog.INFO)
	kiLog.state('YiData', kiLog.INFO)

	dataLen=[0]

	t1= [time.time()]
	def metaCB(_res):
		if not t1[0]:
			t1[0]= time.time()

		logging.info(_res)

	def dataCB(_res):
		dataLen[0]+= len(_res)


	yi= SourceYi4k.YiReader()
	threading.Timer(10, yi.stop).start()
	yiReaderRes= yi.start(dataCB, metaCB)

	logging.info('YiReader: %s, %d rate' % (yiReaderRes, dataLen[0]/(time.time()-t1[0])))



#start-stop camera
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



#yi4k source: start camera and decode stream
def t5():
	kiLog.state('Yi4k', kiLog.DEBUG)
	kiLog.state('YiReader', kiLog.DEBUG)

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



#open-close Streamer
def t6():
	kiLog.state('Streamer', kiLog.INFO)

	streamer= MediaStream.Streamer('test.flv')
	streamerRes= streamer.close()

	logging.info('Streamer: %s' % streamerRes)



#Sink from existing .flv
def t7():
	kiLog.state('SinkRTMP', kiLog.DEBUG)

	sink= MediaStream.SinkRTMP('rtmp://a.rtmp.youtube.com/live2/..')
	with open('test.flv', 'rb') as f:
		sink.add(f.read())

	time.sleep(2)
	sink.close()

	logging.info('SinkRTMP ok')




#Mux and sink from .mp4
import os
def t8():
	origFile= 'test-v/1cam.mp4'
	if not os.path.isfile(origFile):
		return


	kiLog.state('MuxFLV', kiLog.DEBUG)
	kiLog.state('Mp4Recover', kiLog.DEBUG)

	sink= MediaStream.SinkFile('tmp.flv')
	mux= MediaStream.MuxFLV(sink)
	decoder= SourceYi4k.Mp4Recover(mux.add)
	with open(origFile, 'rb') as f:
		while True:
			b= f.read(524288)
			if not b:
				break
			decoder.add(b,1)

	sink.close()

	logging.info('MuxFLV ok')



#Stream from camera to sink.
def t9():
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




def test(fn):
	kiLog.state(False, kiLog.ERROR)
	kiLog.state('', kiLog.INFO)
	fn()
	print()


test(t9)


logging.info('End')
