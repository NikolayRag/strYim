import socket, json, time, re

from kiLog import *



'''
Lightweighted version of Yi4k API, reverse-engineered from official Java API.
It is limited so:
	- values provided to commands should be correct strings,
	- camera data exchanging operations are blocking,
	- no callbacks are supported.

Commands not implemented:

	formatSDCard
		NSFW

	deleteFile
		Considered vulnerable, maybe later

	downloadFile
	cancelDownload
		Redundant, available by http

	getRtspURL
		Redundant, available at YiAPI() creation

	buildLiveVideoQRCode
		Maybe later

	startRecording datetime
		Lazy to implement

'''



'''
Class usable to pass to YiAPI.cmd()

	_params
		dict of non-changing parameters.

	_names
		name or list of names to be assigned later with apply()
'''
class YiAPICommand():
	resultCB= None

	params= None
	names= None

	def __init__(self, _id, _params=None, _names=[], resultCB=None):
		self.resultCB= resultCB

		self.params= {'msg_id':int(_id)}
		if _params:
			self.params.update(_params)

		if not isinstance(_names, list) and not isinstance(_names, tuple):
			_names= [_names]

		self.names= _names


	'''
	Collect dict to be send to camera.
	Append stored params to provided dict and apply _val to stored .names respectively

	Return complete suitable dict.
	'''
	def apply(self, _dict, _val=None):
		_dict.update(self.params)


		#assign provided _val[] values to stored .names[] parameters
		if not isinstance(_val, list) and not isinstance(_val, tuple):
			_val= [_val]

		for pair in zip(self.names,_val):
			_dict[pair[0]]= pair[1]


		return _dict




class YiAPI():
	startSession= YiAPICommand(257)
	stopSession= YiAPICommand(258)


	startRecording=		YiAPICommand(513)
	stopRecording=		YiAPICommand(514)
	capturePhoto=		YiAPICommand(16777220, {'param':'precise quality;off'})
	getFileList=		YiAPICommand(1282, {'param':'/tmp/fuse_d'}, resultCB= lambda res: res['listing'])
#	deleteFile=		YiAPICommand(1281, {}, {'param': '/tmp/fuse_d/DCIM'}, resultCB= lambda res: res['listing'])
	startViewFinder=		YiAPICommand(259)
	stopViewFinder=		YiAPICommand(260)


	getSettings=		YiAPICommand(3, resultCB=lambda res:{key:val for d in res['param'] for key,val in d.items()})
	#"yyyy-MM-dd HH:mm:ss"
	setDateTime=		YiAPICommand(2, {'type':'camera_clock'}, 'param')
	#"capture", "record"
	setSystemMode=		YiAPICommand(2, {'type':'system_mode'}, 'param')
	#"3840x2160 30P 16:9", "3840x2160 30P 16:9 super", "2560x1920 30P 4:3", "1920x1440 60P 4:3", "1920x1440 30P 4:3", "1920x1080 120P 16:9", "1920x1080 120P 16:9 super", "1920x1080 60P 16:9", "1920x1080 60P 16:9 super", "1920x1080 30P 16:9", "1920x1080 30P 16:9 super", "1280x960 120P 4:3", "1280x960 60P 4:3", "1280x720 240P 16:9", "1280x720 120P 16:9 super", "1280x720 60P 16:9 super", "840x480 240P 16:9"
	getVideoResolution=		YiAPICommand(1, {'type':'video_resolution'})
	setVideoResolution=		YiAPICommand(2, {'type':'video_resolution'}, 'param')
	#"12MP (4000x3000 4:3) fov:w", "7MP (3008x2256 4:3) fov:w", "7MP (3008x2256 4:3) fov:m", "5MP (2560x1920 4:3) fov:m", "8MP (3840x2160 16:9) fov:w"
	getPhotoResolution=		YiAPICommand(1, {'type':'photo_size'})
	setPhotoResolution=		YiAPICommand(2, {'type':'photo_size'}, 'param')
	#"auto", "native", "3000k", "5500k", "6500k"
	getPhotoWhiteBalance=		YiAPICommand(1, {'type':'iq_photo_wb'})
	setPhotoWhiteBalance=		YiAPICommand(2, {'type':'iq_photo_wb'}, 'param')
	#"auto", "native", "3000k", "5500k", "6500k"
	getVideoWhiteBalance=		YiAPICommand(1, {'type':'iq_video_wb'})
	setVideoWhiteBalance=		YiAPICommand(2, {'type':'iq_video_wb'}, 'param')
	#"auto", "100", "200", "400", "800", "1600", "6400"
	getPhotoISO=		YiAPICommand(1, {'type':'iq_photo_iso'})
	setPhotoISO=		YiAPICommand(2, {'type':'iq_photo_iso'}, 'param')
	#"auto", "100", "200", "400", "800", "1600", "6400"
	getVideoISO=		YiAPICommand(1, {'type':'iq_video_iso'})
	setVideoISO=		YiAPICommand(2, {'type':'iq_video_iso'}, 'param')
	#"-2.0", "-1.5", "-1.0", "-0.5", "0", "+0.5", "+1.0", "+1.5", "+2.0"
	getPhotoExposureValue=		YiAPICommand(1, {'type':'iq_photo_ev'})
	setPhotoExposureValue=		YiAPICommand(2, {'type':'iq_photo_ev'}, 'param')
	#"-2.0", "-1.5", "-1.0", "-0.5", "0", "+0.5", "+1.0", "+1.5", "+2.0"
	getVideoExposureValue=		YiAPICommand(1, {'type':'iq_video_ev'})
	setVideoExposureValue=		YiAPICommand(2, {'type':'iq_video_ev'}, 'param')
	#"auto", "2s", "5s", "10s", "20s", "30s"
	getPhotoShutterTime=		YiAPICommand(1, {'type':'iq_photo_shutter'})
	setPhotoShutterTime=		YiAPICommand(2, {'type':'iq_photo_shutter'}, 'param')
	#"low", "medium", "high"
	getVideoSharpness=		YiAPICommand(1, {'type':'video_sharpness'})
	setVideoSharpness=		YiAPICommand(2, {'type':'video_sharpness'}, 'param')
	#"low", "medium", "high"
	getPhotoSharpness=		YiAPICommand(1, {'type':'photo_sharpness'})
	setPhotoSharpness=		YiAPICommand(2, {'type':'photo_sharpness'}, 'param')
	#"wide", "medium", "narrow"
	getVideoFieldOfView=		YiAPICommand(1, {'type':'fov'})
	setVideoFieldOfView=		YiAPICommand(2, {'type':'fov'}, 'param')
	#"record", "record_timelapse", "record_slow_motion", "record_loop", "record_photo"
	getRecordMode=		YiAPICommand(1, {'type':'rec_mode'})
	setRecordMode=		YiAPICommand(2, {'type':'rec_mode'}, 'param')
    #Normal:"precise quality", Timer:"precise self quality", Burst:"burst quality", Timelapse:"precise quality cont."
	getCaptureMode=		YiAPICommand(1, {'type':'capture_mode'})
	setCaptureMode=		YiAPICommand(2, {'type':'capture_mode'}, 'param')
	#"center", "average", "spot"
	getMeteringMode=		YiAPICommand(1, {'type':'meter_mode'})
	setMeteringMode=		YiAPICommand(2, {'type':'meter_mode'}, 'param')
	#"S.Fine", "Fine", "Normal"
	getVideoQuality=		YiAPICommand(1, {'type':'video_quality'})
	setVideoQuality=		YiAPICommand(2, {'type':'video_quality'}, 'param')
	#"yi", "flat"
	getVideoColorMode=		YiAPICommand(1, {'type':'video_flat_color'})
	setVideoColorMode=		YiAPICommand(2, {'type':'video_flat_color'}, 'param')
	#"yi", "flat"
	getPhotoColorMode=		YiAPICommand(1, {'type':'photo_flat_color'})
	setPhotoColorMode=		YiAPICommand(2, {'type':'photo_flat_color'}, 'param')
	#"on", "off"
	getElectronicImageStabilizationState=		YiAPICommand(1, {'type':'iq_eis_enable'})
	setElectronicImageStabilizationState=		YiAPICommand(2, {'type':'iq_eis_enable'}, 'param')
	#"on", "off"
	getAdjustLensDistortionState=		YiAPICommand(1, {'type':'warp_enable'})
	setAdjustLensDistortionState=		YiAPICommand(2, {'type':'warp_enable'}, 'param')
	#"on", "off"
	getVideoMuteState=		YiAPICommand(1, {'type':'video_mute_set'})
	setVideoMuteState=		YiAPICommand(2, {'type':'video_mute_set'}, 'param')
	#"off", "time", "date", "date/time"
	getVideoTimestamp=		YiAPICommand(1, {'type':'video_stamp'})
	setVideoTimestamp=		YiAPICommand(2, {'type':'video_stamp'}, 'param')
	#"off", "time", "date", "date/time"
	getPhotoTimestamp=		YiAPICommand(1, {'type':'photo_stamp'})
	setPhotoTimestamp=		YiAPICommand(2, {'type':'photo_stamp'}, 'param')
	#"all enable", "all disable", "status enable"
	getLEDMode=		YiAPICommand(1, {'type':'led_mode'})
	setLEDMode=		YiAPICommand(2, {'type':'led_mode'}, 'param')
	#"PAL", "NTSC"
	getVideoStandard=		YiAPICommand(1, {'type':'video_standard'})
	setVideoStandard=		YiAPICommand(2, {'type':'video_standard'}, 'param')
	#"0.5", "1", "2", "5", "10", "30", "60"
	getTimeLapseVideoInterval=		YiAPICommand(1, {'type':'timelapse_video'})
	setTimeLapseVideoInterval=		YiAPICommand(2, {'type':'timelapse_video'}, 'param')
	#"continue", "0.5 sec", "1.0 sec", "2.0 sec", "5.0 sec", "10.0 sec", "30.0 sec", "60.0 sec", "2.0 min", "5.0 min", "10.0 min", "30.0 min", "60.0 min"
	getTimeLapsePhotoInterval=		YiAPICommand(1, {'type':'precise_cont_time'})
	setTimeLapsePhotoInterval=		YiAPICommand(2, {'type':'precise_cont_time'}, 'param')
	#"off", "6s", "8s", "10s", "20s", "30s", "60s", "120s"
	getTimeLapseVideoDuration=		YiAPICommand(1, {'type':'timelapse_video_duration'})
	setTimeLapseVideoDuration=		YiAPICommand(2, {'type':'timelapse_video_duration'}, 'param')
	#"never", "30s", "60s", "120s"
	getScreenAutoLock=		YiAPICommand(1, {'type':'screen_auto_lock'})
	setScreenAutoLock=		YiAPICommand(2, {'type':'screen_auto_lock'}, 'param')
	#"off", "3 minutes", "5 minutes", "10 minutes"
	getAutoPowerOff=		YiAPICommand(1, {'type':'auto_power_off'})
	setAutoPowerOff=		YiAPICommand(2, {'type':'auto_power_off'}, 'param')
	#"off", "on", "auto"
	getVideoRotateMode=		YiAPICommand(1, {'type':'video_rotate'})
	setVideoRotateMode=		YiAPICommand(2, {'type':'video_rotate'}, 'param')
	#"high", "low", "mute"
	getBuzzerVolume=		YiAPICommand(1, {'type':'buzzer_volume'})
	setBuzzerVolume=		YiAPICommand(2, {'type':'buzzer_volume'}, 'param')
	#"5 minutes", "20 minutes", "60 minutes", "120 minutes", "max"
	getLoopDuration=		YiAPICommand(1, {'type':'loop_rec_duration'})
	setLoopDuration=		YiAPICommand(2, {'type':'loop_rec_duration'}, 'param')



	jsonTest= re.compile('Extra data: line \d+ column \d+ - line \d+ column \d+ \(char (?P<char>\d+) - \d+\)')

	ip= '192.168.42.1'
	sock= None
	tick= 0
	sessionId= 0

	res= []



	@staticmethod
	def defaults(ip):
		if ip:
			YiAPI.ip= ip



	def __init__(self, _ip=None):
		if _ip:
			self.ip= _ip
		try:
			self.sock= socket.create_connection((self.ip,7878),3)
		except:
			self.res= False
			return

		res= self.cmd(YiAPI.startSession)
		if res<0:
			self.sock= None
			self.res= False
		else:
			self.sessionId= res


	#shoud be called at very end to tell camera it's released
	def close(self):
		self.cmd(YiAPI.stopSession)

		self.sock= None



	'''
	Run predefined _command.
	if _vals provided, it's a value assigned to YiAPICommand.vals respectively. 
	'''
	def cmd(self, _command, _val=None):
		if not self.sock:
			kiLog.err('Camera disconnected')
			return -99999


		self.cmdSend(_command, _val)
		self.res= self.jsonRestore( self.cmdRecv() )
		if not self.res:
			kiLog.err('Invalid response')
			return -99998


		res= {'rval':0}
		if len(self.res):
			for res in self.res:	#find block with rval
				if 'rval' in res:
					break


		if 'rval' in res and res['rval']:
			kiLog.err('Camera error: %d' % res['rval'])
			kiLog.verb('Full result: %s' % str(self.res))
			return res['rval']

		if callable(_command.resultCB):
			return _command.resultCB(res)

		if 'param' in res:
			return res['param']



	'''
	Sent _command co camera.
	'''
	def cmdSend(self, _command, _val=None):
		out= _command.apply({'token':self.sessionId, 'heartbeat':self.tick}, _val)

		kiLog.verb("Send: %s" % out)
		
		self.sock.sendall( bytes(json.dumps(out),'ascii') )

		self.tick+= 1



	'''
	Recieve string from socket till its dry.
	'''
	def cmdRecv(self):
		self.sock.settimeout(2)	#wait for a while for camera to execute command
		res= b''

		while True:
			try:
				recv= self.sock.recv(4096)
				res+= recv

				kiLog.verb("part: %s" % recv)

				self.sock.settimeout(.1) #wait a little for detect end-of-data
			except:
				break

		kiLog.verb("Recieved: %d bytes" % len(res))

		return res.decode()



	'''
	Form array of json-restored values from string containing several json-encoded blocks
	'''
	def jsonRestore(self, _json):
		jsonA= []

		jsonFrom= 0
		while True:
			try:
				jsonTry= json.loads(_json[jsonFrom:])
				jsonA.append(jsonTry)	#rest
				break	#json ended up
			except Exception as exc:
				kiLog.verb('Json result: ' +str(exc))
				
				jsonErr= self.jsonTest.match(str(exc))
				if not jsonErr:
					return False

				jsonFrom2= int(jsonErr.group('char'))
				jsonA.append( json.loads(_json[jsonFrom:jsonFrom+jsonFrom2]) )

				jsonFrom+= jsonFrom2


		return(jsonA)
