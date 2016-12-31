# Stryim
No-recompression HD RTMP streaming for Yi 4K.

Stryim read video/audio stream from camera and send it to RTMP server, i.e. Youtube, Facebook, Twitch etc.  
The quality and bitrate of the stream sent is exactly the one that camera records to flash.

**Download compiled executable: [stryim.zip](https://github.com/NikolayRag/strYim/files/679658/stryim.zip)**  
This is development test version, so using it requires little of user action.

### Prerequisites
Things to be checked once:
- You must have two network interfaces on PC running Stryim: (1) WiFi connected to camera, (2) connection to Internet,
- enable 8081-8089 ports in firewall or disable firewall for WiFi (will be obsolete in next version),
- create blank `console_enable.script` in camera flash's root.

### Using
Make sure prerequisites match, connect PC's Wifi to camera.

Run `stryim.exe rtmp://server/path [-nonstop]`.  
Camera then will go in record state and streaming will start.  
For Youtube use `rtmp://a.rtmp.youtube.com/live2/your-secret-key` server/path.

To stop streaming just stop camera of press `Control-C`.

If `-nonstop` specified, Stryim will remain running when you pause/unpause camera.  
Please dont manualy change camera settings while in pause.

### Limits and issues
While the minimal bitrate from camera is about 13mbits/sec, destination server could cut the band to its limit.  
For example, Youtube limit 1080 HD to 6mbits/sec.

The only one resolution supported so far is 1920x1080 30fps.

No Camera/Internet bandwidth checking is performed so far, so try to hold camera not too far from PC.

