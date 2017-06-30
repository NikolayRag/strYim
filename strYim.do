!test 2: +0 "src\kiTelnet.py" kii 16/10/28 20:48:47
	test

!network, unsure 6: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiTelnet.py" kii 16/11/05 23:18:34
	think of telnet over route

+network 7: +1 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiTelnet.py" kii 16/10/28 23:26:41
	start sending telnet ONLY after TCP started listening

 telnet 8: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiTelnet.py" kii 16/11/21 00:49:41
	check for timeout

+code 11: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiTelnet.py" kii 16/10/29 20:09:13
	call telnet unblocking

!clean, network 16: +0 "" kii 16/10/31 06:45:59
	outdated

+clean, network 17: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiYiListener.py" kii 16/10/29 21:29:24
	make sure KiTelnet recreated

+telnet 19: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiTelnet.py" kii 16/11/01 15:15:06
	get telnet finish elseway

+telnet, log 20: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiTelnet.py" kii 16/10/30 15:53:35
	use log elseway

!telnet 23: +0 "" kii 16/10/31 03:58:52
	add timeout for blankNone

+read, cam 31: +1 "src\appStreamer\yiAgent.py" kii 17/01/05 03:14:45
	check 999+ file switch

 read, cam 33: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiYiListener.py" kii 16/11/04 20:21:34
	detect buffer overrun

 read, cam 34: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiYiListener.py" kii 16/11/04 20:21:54
	detect buffer underrun

+transit 35: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\byteTransit.py" kii 16/11/05 04:51:40
	add trigger functionality

+transit, clean 37: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\byteTransit.py" kii 16/11/05 18:07:26
	remove dried context more precisely

+cam 39: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiYiListener.py" kii 16/11/06 00:41:16
	add on-off, live-dead callbacks to start()

+cam 40: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiYiListener.py" kii 16/11/06 00:44:37
	add mp4Buffer argument to live()

!cam 41: +0 "" kii 16/11/06 00:45:39
	spoiled

+recover 44: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\stryim.py" kii 16/11/07 03:33:04
	move start position as data recovered

+stage 46: +0 "" kii 16/11/06 15:45:43
	stage: continuous read

+stage 47: +0 "" kii 16/11/07 05:24:32
	stage: recover

+stage 48: +0 "" kii 16/11/21 00:52:19
	stage: mux

+stage, output 49: +0 "" kii 17/05/18 09:31:17
	stage: send to rtmp

-stage, output 50: +0 "" kii 16/11/06 15:47:34
	stage: rtmp server

 cam 53: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiYiListener.py" kii 16/11/07 02:49:46
	force kill data sending at dead()

+recover, callback 55: +1 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4RecoverExe.py" kii 16/11/08 19:21:09
	send atom data, not only meta

+speed, bytes 61: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\byteTransit.py" kii 16/11/08 17:15:04
	dont use adding bytes

 speed, bytes 62: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\byteTransit.py" kii 16/11/30 19:12:37
	read more quickly maybe

!general 63: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4RecoverExe.py" kii 16/11/09 10:34:21
	

+mp4 64: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4RecoverExe.py" kii 16/11/16 23:20:08
	allow start only from IDR frame

 cam, stability 68: -1 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiYiListener.py" kii 16/11/10 02:46:42
	found other way to forget stopped file as live

!mp4 79: +0 "" kii 16/11/20 15:04:24
	redundant

!flv 90: +0 "" kii 17/05/29 19:42:00
	not needed

+flv 91: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\stryim.py" kii 16/11/20 01:28:05
	construct AVCDecoderConfigurationRecord

+flv 92: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\stryim.py" kii 16/11/19 07:15:35
	make class non-static

+flv 93: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\stryim.py" kii 16/11/19 08:23:59
	make data flow without overhead

+app 94: +2 "..\..\Application Data\Sublime Text 3\Packages\stryim\stryim.py" kii 16/11/26 06:40:45
	handle start-stops

+bytes 95: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4RecoverExe.py" kii 16/11/21 01:57:58
	move use of byteTransit inside mp4RecoverExe

+flv 98: +0 "src\MediaStream\Mux.py" kii 17/05/30 04:22:40
	Init stream with SPS and PPS provided

!aac 99: +1 "" kii 16/11/23 03:54:25
	become todo 108

!aac 100: +0 "" kii 16/11/20 15:04:38
	redundant

+recover 101: +2 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4Recover.py" kii 16/12/04 08:37:21
	use native atoms searching: [h264, aac, ...]

+bytes 102: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\byteTransit.py" kii 16/11/21 01:23:24
	make .add() the single public method

+clean, release 104: +0 "src\MediaStream\Sink.py" kii 17/05/21 20:11:07
	hide ffmpeg output

 sink, unsure 105: -1 "src\MediaStream\Sink.py" kii 17/05/21 20:11:09
	hardcode RTMP protocol

+test, recover 107: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4Recover.py" kii 16/11/26 06:37:00
	collect all interframe AAC into one

+aac 108: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\muxH264AAC.py" kii 16/12/11 00:24:15
	write (optional) ADTS header

-read, cam 114: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\yiListener.py" kii 16/11/25 03:26:03
	define maximum read block

 mux, flv, bytes, aac 117: -1 "src\MediaStream\Atom.py" kii 17/05/06 20:47:38
	reveal actual AAC frame length

!sink 118: +0 "src\MediaStream\Sink.py" kii 17/05/18 11:57:37
	make SinkTCP nonblocking, stream-based

!sink 119: +0 "src\MediaStream\Sink.py" kii 17/05/18 11:57:43
	make SinkRTMP nonblocking, stream-based

+ui 120: +0 "src\__main__w.py" kii 17/05/22 07:35:16
	add ui

+log 121: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiLog.py" kii 16/11/26 15:28:27
	add 'verb' level and .verb()

+recover, clean 122: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4Recover.py" kii 16/11/28 18:41:18
	remove after going native

+clean 123: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4Recover.py" kii 16/12/04 23:12:28
	remove ctx arg

!recover, mp4 124: +0 "" kii 16/12/04 08:28:29
	obsolete

-bytes 128: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4Recover.py" kii 16/12/04 08:37:08
	use memoryview as binded data

+optimize 140: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\kiSupport.py" kii 16/12/13 01:45:34
	OPTIMIZE

!feature 177: -1 "..\..\Application Data\Sublime Text 3\Packages\stryim\AACCore.py" kii 16/12/18 19:23:51
	decode ATDS AAC

 feature 178: -1 "..\..\Application Data\Sublime Text 3\Packages\stryim\AACCore.py" kii 16/12/19 00:48:53
	read ADTS header, bitstream seek() must be implemented

!feature 179: -1 "..\..\Application Data\Sublime Text 3\Packages\stryim\AACCore.py" kii 17/05/21 20:17:17
	not-common_window

 feature, aac 180: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\mp4Recover.py" kii 16/12/21 04:59:20
	detect AAC length by native decoding

 feature, aac, clean 181: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\AACCore.py" kii 16/12/20 17:15:58
	remove after full decoding done

 feature, aac 182: -1 "..\..\Application Data\Sublime Text 3\Packages\stryim\AACCore.py" kii 16/12/20 17:16:33
	add different aac types

 aac 183: +0 "..\..\Application Data\Sublime Text 3\Packages\stryim\AACSupport.py" kii 16/12/20 17:33:11
	fill VLC table

!feature, ui 200: +0 "" kii 17/01/09 03:27:40
	outdated

+fix, aac 202: +1 "..\..\Application Data\Sublime Text 3\Packages\stryim\AACDetect.py" kii 16/12/22 21:25:13
	make possible to start AAC queue NOT from max_sfb=0

 app, feature, unsure 218: +0 "src\Ui\Ui.py" ki 17/06/30 22:23:16
	allow reconfiguration

!app, clean, feature 219: +0 "" kii 17/01/03 01:05:20
	redundant

+Yi 225: +0 "src\appControl\yiControl.py" kii 17/04/10 03:26:23
	detect real command ending

+Yi, fix 227: +0 "src\yiListener.py" kii 17/05/20 15:32:39
	deleted files remains in camera file list till restart

+Yi, fix 228: +0 "src\SourceYi4k\YiControl\YiControl.py" kii 17/05/07 11:56:55
	detect Yi4kAPI errors: playback mode, busy switching

+Yi 229: +0 "src\yiControl.py" kii 16/12/31 05:23:30
	set loop length to 5min

+Yi 230: +0 "src\SourceYi4k\YiControl\YiControl.py" kii 17/05/07 04:23:52
	detect error when stopping stopped cam

!Yi 232: +0 "" kii 17/05/18 10:05:23
	obsolete

+gui, feature 235: +0 "src\stryim.py" kii 17/01/08 22:19:47
	store and reuse settings

+gui, feature 236: +0 "src\stryim.py" kii 17/01/09 03:52:46
	accept commandline settings

+Yi, core 237: +1 "src\MediaStream\MediaStreamer.py" kii 17/05/08 05:30:04
	make agent to run at Yi side

+app, clean 238: +1 "src\__main__.py" kii 17/05/20 15:30:20
	simplify cmdline flow

-gui, feature 239: -1 "src\Ui\AppWindow.py" ki 17/06/30 22:15:07
	make customizable destination list 

+ 240: +0 "" kii 17/05/20 15:32:51
	catch keyboard interrupt at blocked network operations

 gui, feature 241: +0 "src\appGui\gui.py" kii 17/01/09 02:31:26
	add/remove sources

!feature 242: +0 "src\Ui\Ui.py" kii 17/05/22 06:35:57
	check destination

!feature, v2 244: -1 "" kii 17/05/18 10:05:01
	obsolete

+feature, YiAgent 257: +0 "src\SourceYi4k\YiReader.py" kii 17/04/25 22:45:00
	Send agent to camera

+feature, YiAgent 258: +0 "src\SourceYi4k\YiReader.py" kii 17/04/25 22:45:02
	Run agent at camera

+feature, YiAgent 259: +0 "src\SourceYi4k\YiAgent.py" kii 17/04/25 22:49:58
	Make camera agent

+YiAgent, check 260: +0 "src\SourceYi4k\YiReader.py" kii 17/05/02 04:07:05
	catch recording stops or cannot start

 YiAgent, check 261: +0 "src\SourceYi4k\__init__.py" kii 17/05/20 21:56:43
	set camera settings

 telnet 262: -1 "src\appStreamer\kiTelnet.py" kii 17/04/19 01:50:05
	detect self ip for any mask

+telnet 264: +0 "src\kiTelnet\src\KiTelnet.py" kii 17/04/21 03:41:22
	add nonblocking result callback

!YiAgent, check 265: +1 "" kii 17/05/04 03:36:17
	move to 268 (telnet connection timeout)

+YiAgent, check 266: +1 "src\SourceYi4k\__init__.py" kii 17/05/20 21:56:42
	check camera die

+YiAgent, check 267: +0 "src\SourceYi4k\YiReader.py" kii 17/05/04 00:43:27
	handle yiClose() for idle YiAgent

+telnet, clean 268: +0 "src\KiTelnet\KiTelnet.py" kii 17/05/04 03:49:03
	set connection only timeout

+telnet, fix 269: +1 "src\SourceYi4k\YiPy.py" kii 17/05/04 04:33:47
	timeing out telnet before YiPy listener timeout results in hang

-YiAgent, clean 270: +0 "src\SourceYi4k\YiSide\YiAgent.py" kii 17/05/04 04:48:23
	detect only file which grown in current session

 Yi, config 272: +0 "src\SourceYi4k\Yi4k.py" kii 17/05/07 03:09:22
	add 60 fps

 Yi, config 273: +0 "src\SourceYi4k\Yi4k.py" kii 17/05/07 03:09:32
	add 1440 format

+Yi, control 274: +0 "src\SourceYi4k\Yi4k.py" kii 17/05/07 11:57:12
	dont start if camera started

+Yi, control 275: +0 "src\SourceYi4k\Yi4k.py" kii 17/05/07 11:57:07
	stop if camera stops

+Yi, fix 276: +0 "src\SourceYi4k\YiControl\YiControl.py" kii 17/05/18 11:56:14
	update YiAPI and place it in YiControl

+Yi, clean 277: +0 "src\SourceYi4k\YiControl\YiControl.py" kii 17/05/07 14:05:47
	remove recorded video files

+Yi, fix 278: +0 "src\test.py" kii 17/05/20 18:02:54
	immedeate stop after start fails

+Yi 279: +0 "src\SourceYi4k\YiControl\YiControl.py" kii 17/05/07 04:28:13
	dont release YiAPI object until stop()

+Yi 280: +0 "src\SourceYi4k\YiControl\YiControl.py" kii 17/05/07 11:27:46
	detect explicit camera stop

+YiAgent, clean, fix 281: +0 "src\SourceYi4k\YiControl\YiControl.py" kii 17/05/20 15:32:04
	release last file for deletion

+Yi, control, fix 282: +0 "src\test.py" kii 17/05/08 04:07:19
	handle camera settings error

 feature, streaming 283: +0 "src\MediaStream\Streamer.py" kii 17/05/08 23:21:33
	define Source abstract superclass.

 feature, streaming 284: +0 "src\MediaStream\Streamer.py" kii 17/05/15 02:44:11
	Make audio/video mixer (switcher) as a Source-to-Streamer fabric

+recover, fix 285: +0 "src\SourceYi4k\YiDecoder\MP4Recover.py" kii 17/05/16 06:40:43
	repair jugged result

+YiAgent, fix 286: +1 "src\SourceYi4k\YiReader\YiSide\YiAgent.py" kii 17/05/13 08:59:59
	reading block implicitly to the end of growing file causes data distort

+streaming, fix 288: +0 "src\MediaStream\Streamer.py" kii 17/05/15 02:46:10
	ulink source before linking other

+streaming, fix, ffmpeg, exploit 289: +2 "src\MediaStream\Streamer.py" kii 17/05/16 06:33:36
	incoming data skipped if mux/sink delayed in the same thread; possibly issue of interfering with YiReader reciever loop

+streaming, fix, ffmpeg, exploit 290: +1 "src\SourceYi4k\YiReader\YiReader.py" kii 17/05/21 05:33:36
	/289; separate thread; streaming to rtmp cause reading delay

 mux 291: +0 "src\MediaStream\Streamer.py" kii 17/05/18 09:23:22
	/98; (re)init muxer with sps/pps provided from source

!Yi 293: +0 "src\SourceYi4k\Yi4k.py" kii 17/05/18 11:03:30
	add force

+YiAgent, clean 295: +0 "src\SourceYi4k\YiReader\YiSide\YiAgent.py" kii 17/05/19 00:27:02
	remove delay at stop

 Yi, fix 296: +0 "src\SourceYi4k\YiControl\YiControl.py" kii 17/05/19 01:02:26
	camera stopped after stop sometimes

+YiAgent, fix, clean 297: +0 "src\SourceYi4k\YiReader\YiSide\YiCleanup.py" kii 17/05/20 03:13:34
	Cleanup hangs sometimes

+clean 299: +0 "src\__main__.py" kii 17/05/20 17:48:47
	Show general console messages

+YiAgent, fix 300: +0 "src\SourceYi4k\YiReader\YiReader.py" kii 17/05/21 05:06:43
	catch error on sudden disconnect

+YiAgent, fix, network 301: +2 "src\SourceYi4k\YiReader\YiSide\YiSock.py" kii 17/05/21 06:10:25
	settimg timeout breaks entire transfer

+log, clean 302: +0 "src\__main__.py" kii 17/05/22 00:09:55
	add runtime significant logging

-ui, settings 304: +0 "src\Ui\AppWindow.py" kii 17/05/23 00:02:16
	make updatable settings model

-clean, sink 305: +0 "src\MediaStream\Sink.py" kii 17/05/28 18:14:12
	autodetect free port for ffmpeg

-clean, YiAgent 306: +0 "src\SourceYi4k\YiReader\YiSide\YiCleanup.py" kii 17/05/28 10:00:31
	stop camera and restore settings in YiCleanup

=streaming, mux, sink 307: +0 "src\MediaStream\Streamer.py" kii 17/05/30 04:25:25
	Get stream prefix from source

+streaming, sink 308: +0 "src\MediaStream\Sink.py" kii 17/05/30 05:35:18
	allow reconnection

+streaming, sink 309: +0 "src\MediaStream\Sink.py" kii 17/05/30 06:40:47
	jitter issue if connected with pause

-YiAgent, log 310: +0 "src\SourceYi4k\YiReader\YiSide\YiAgent.py" kii 17/05/30 18:07:38
	inform of current state more verbosely

+Yi, recover 311: +2 "src\SourceYi4k\YiDecoder\MP4Recover.py" kii 17/06/28 06:07:48
	fix lost frames at end block

+Yi, recover 316: +0 "src\SourceYi4k\YiDecoder\MP4Recover.py" ki 17/06/28 05:17:03
	manage loop gaps

+YiAgent, read 318: +0 "src\SourceYi4k\YiReader\YiSide\YiAgent.py" ki 17/06/28 05:08:11
	read liveBlocks in cycle while available

+YiAgent, read 319: +0 "src\SourceYi4k\YiReader\YiSide\YiAgent.py" ki 17/06/28 05:07:57
	readBlock() reads and sends data

+Yi, recover 320: +0 "src\SourceYi4k\YiReader\YiSide\YiAgent.py" ki 17/06/29 00:42:22
	catch flat mode file chain

=Yi, agent 321: +2 "src\SourceYi4k\YiReader\YiReader.py" ki 17/06/30 02:05:47
	make Reader reading HTTP, as it's become available

+Yi, clean, fix 322: +2 "src\SourceYi4k\YiReader\YiSide\YiCleanup.py" ki 17/06/29 05:41:21
	subsequent flat files dont delete

-args, sink 323: +0 "src\MediaStream\Sink.py" ki 17/06/29 05:45:04
	add TCP buffer size arg

-args 324: +0 "src\args.py" ki 17/06/29 05:46:15
	add bandwidth test arg

=app, feature, gui 325: +0 "src\Ui\Ui.py" ki 17/06/30 22:24:02
	show state

=app, check 326: +0 "src\Ui\Ui.py" ki 17/06/30 22:24:46
	inspect header passing when restoring camera/stream

