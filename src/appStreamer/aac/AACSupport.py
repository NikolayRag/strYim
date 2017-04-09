class AACStatic():
	#consts

#	AOT_NULL=	0
#	AOT_AAC_MAIN=	1
	AOT_AAC_LC=	2
#	AOT_AAC_SSR=	3
#	AOT_AAC_LTP=	4
#	AOT_SBR=	5
#	AOT_AAC_SCALABLE=	6
#	AOT_TWINVQ=	7
#	AOT_CELP=	8
#	AOT_HVXC=	9
#	AOT_TTSI=	12
#	AOT_MAINSYNTH=	13
#	AOT_WAVESYNTH=	14
#	AOT_MIDI=	15
#	AOT_SAFX=	16
#	AOT_ER_AAC_LC=	17
#	AOT_ER_AAC_LTP=	19
#	AOT_ER_AAC_SCALABLE=	20
#	AOT_ER_TWINVQ=	21
#	AOT_ER_BSAC=	22
#	AOT_ER_AAC_LD=	23
#	AOT_ER_CELP=	24
#	AOT_ER_HVXC=	25
#	AOT_ER_HILN=	26
#	AOT_ER_PARAM=	27
#	AOT_SSC=	28
#	AOT_PS=	29
#	AOT_SURROUND=	30
#	AOT_ESCAPE=	31
#	AOT_L1=	32
#	AOT_L2=	33
#	AOT_L3=	34
#	AOT_DST=	35
#	AOT_ALS=	36
#	AOT_SLS=	37
#	AOT_SLS_NON_CORE=	38
#	AOT_ER_AAC_ELD=	39
#	AOT_SMR_SIMPLE=	40
#	AOT_SMR_MAIN=	41
#	AOT_USAC_NOSBR=	42
#	AOT_SAOC=	43
#	AOT_LD_SURROUND=	44
#	AOT_USAC=	45



#	TYPE_SCE=	0
	TYPE_CPE=	1
#	TYPE_CCE=	2
#	TYPE_LFE=	3
#	TYPE_DSE=	4
#	TYPE_PCE=	5
#	TYPE_FIL=	6
	TYPE_END=	7

#	EXT_FILL=	0
#	EXT_FILL_DATA=	1
#	EXT_DATA_ELEMENT=	2
#	EXT_DYNAMIC_RANGE = 0xb
#	EXT_SBR_DATA      = 0xd
#	EXT_SBR_DATA_CRC  = 0xe


	ONLY_LONG_SEQUENCE=	0
	LONG_START_SEQUENCE=	1
	EIGHT_SHORT_SEQUENCE=	2
	LONG_STOP_SEQUENCE=	3

	ZERO_BT        = 0
	FIRST_PAIR_BT  = 5
	ESC_BT         = 11
	RESERVED_BT    = 12
	NOISE_BT       = 13
	INTENSITY_BT2  = 14
	INTENSITY_BT   = 15

	AAC_CHANNEL_OFF   = 0
	AAC_CHANNEL_FRONT = 1
	AAC_CHANNEL_SIDE  = 2
	AAC_CHANNEL_BACK  = 3
	AAC_CHANNEL_LFE   = 4
	AAC_CHANNEL_CC    = 5



#	MAX_PREDICTORS= 672

#	SCALE_DIV_512=    36
#	SCALE_ONE_POS=   140
#	SCALE_MAX_POS=   255
#	SCALE_MAX_DIFF=   60
	SCALE_DIFF_ZERO=  60

#	POW_SF2_ZERO=    200

	NOISE_PRE=       256
	NOISE_PRE_BITS=    9
	NOISE_OFFSET=     90
  

	sample_rates= [96000, 88200, 64000, 48000, 44100, 32000, 24000, 22050, 16000, 12000, 11025, 8000, 7350]






	#unfinished (unstarted indeed)
#  todo 183 (aac) +0: fill VLC table
	def buildVLC(codes, bits):
		nb_bits= 7
		nb_codes= len(codes)
		
		table= [[0,0]] *352

		return table

	#VLCTable= buildVLC(ff_aac_scalefactor_code, ff_aac_scalefactor_bits)



class MPEG4AudioConfig():
	object_type=	None
	sampling_index=	None
	sample_rate=	None
	chan_config=	None

#	channels=	None
#	sbr=	None
#	ps=	None
#	frame_length_short=	None

#	ext_object_type=	None
#	ext_sampling_index=	None
#	ext_sample_rate=	None
#	ext_chan_config=	None

	def __init__(self, _m4ac=None):
		if _m4ac:
			self.set(
				  object_type= _m4ac.object_type
				, chan_config= _m4ac.chan_config
				, sampling_index= _m4ac.sampling_index
			)


	def set(self, object_type=None, chan_config=None, sampling_index=None):
		self.object_type= object_type
		self.chan_config= chan_config
		self.sampling_index= sampling_index

		self.sampling_rate= AACStatic.sample_rates[self.sampling_index]



class IndividualChannelStream():
	ms_present= 0
	max_sfb= 0
	windows_sequence0= 0
	use_kb_window0= 0
	num_window_groups= 0
	group_len= [0] *8
#	ltp
#	uint8_t *swb_sizes
	num_windows= 0

	swb_offset= 0
	tns_max_bands= 0
	num_swb= 0

	predictor_present= 0
#	predictor_initialized
	predictor_reset_group= 0
#	predictor_reset_count= [None] *31
#	prediction_used= [None] *41
#	window_clipping= [None] *8
#	clip_avoidance_factor


	def __init__(self, _ref=None):
		if _ref:
#			self.use_kb_window0= ref.use_kb_window0
			None



class SingleChannelElement():
	band_type= [0] *128
	band_type_run_end= [0] *120
	sf= [0] *120
#	can_pns= [0] *128
#	pcoeffs= [0] *1024
	coeffs= [0] *1024
#	saved= [0] *1536
#	ret_buf= [0] *2048
#	ltp_state= [0] *3072
#	predictor_state[MAX_PREDICTORS];



	def __init__(self, _ref=None):
		if _ref:
			None



class ChannelElement():
#	present= None

	common_window= 0
	ms_present= 0
#	ms_mode= None
#	is_mode= None
	ms_mask= [0] *128
	is_mask= [0] *128

#	ChannelCoupling coup
#	SpectralBandReplication sbr


class Pulse():
	num_pulse= 0
	start= 0
	pos= [0] *4
	amp= [0] *4


#class AACContext():
#	None

#class AVCodecContext():
#	None

#class AVFrame():
#	None
