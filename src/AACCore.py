from .AACSupport import *
from .kiSupport import *


'''
AAC decoder suitable for detecting particular {AOT_AAC_LC, L+R, CPE} stream.
Indeed it's a very bit of FFMPEG's aac_decode_frame() and further in.
It's far from being a complete decoder and is intended to be an AAC playground.
'''
class AACCore():
	#runtimes
#	avctx= AVCodecContext()	#codec context, shortcut for ac->avctx
#	ac= AACContext() #shortcut for avctx->priv_data
#	ac_frame= AVFrame() #frame data filled back, shortcut for ac->frame AKA data
	ac_m4ac= None #active audion config, shortcut for ac->oc[1].m4ac
	m4ac= MPEG4AudioConfig() #template audion config for ac_m4ac
	ac_che= None #ChannelElement
	sce_ics0= None
	sce_ics1= None

	bits= None	#gb bit context


	#AAC decoded
	error= 0


	'''
	init AAC decoder for subsequental calls.
	Provided audio parameters will be overriden for ADTS frame
	'''
	def __init__ (self, samplingIndex=3):
		self.m4ac.set(
			  object_type= AACStatic.AOT_AAC_LC
			, chan_config= 2	#(L+R)
			, sampling_index= samplingIndex	#reference AACStatic.sample_rates (3=48000)
		)





	'''
	Main entry point. Decode provided (bytes)_data and fills back frame characteristics.
	Original arguments are stored as object variables instead of being passed recursively


	'''
	def aac_decode_frame(self, _data, _once=True):
		self.bits= Bits(_data)
		self.error= 0

		self.ac_m4ac= MPEG4AudioConfig(self.m4ac)


		#aac_decode_frame_int() inlined

#  todo 178 (feature) -1: read ADTS header, bitstream seek() must be implemented
#		if self.bits.get(12) == 0xfff:
#			self.readADTS(self.ac_m4ac)
#		else:
#			self.bits.seek(0)


		while True:
			elem_type= self.bits.get(3)
			if elem_type==AACStatic.TYPE_END:
				break

			aac_id= self.bits.get(4)

			self.ac_che= ChannelElement()
			self.sce_ics0= SCE_ICS()


			#TYPE_CPE is only one supported indeed
			if elem_type == AACStatic.TYPE_CPE:
				self.decode_cpe()

			else:
				self.error= -1


			if self.error:
				break

			if _once or 1: #only one AAC block atm, sorry
				break


		return self



	


	def decode_cpe(self):
		ics= self.sce_ics0

		common_window= self.bits.get(1)
	
#  todo 179 (feature) -1: not-common_window
		if True:	#common_window:
			self.decode_ics_info(ics)
			if self.error:
				return

			self.sce_ics1= SCE_ICS(ics)

			if False:	#ics.predictor_present && self.ac_m4ac.object_type != AOT_AAC_MAIN
				None
				'''
				ics.ltp.present = self.bits.get(1)
				if ics.ltp.present:
					decode_ltp(self.sce_ics1)	#decode other channel
				'''


			ms_present= self.bits.get(2)
			if ms_present==3:	#reserved MS
				self.result= -7
				return

			#+decode_mid_side_stereo
			if ms_present==2:	#all 1
				self.ac_che.ms_mask= [1] *ics.num_window_groups*ics.max_sfb

			if ms_present==1:
				for idx in range(0,ics.num_window_groups*ics.max_sfb):
					self.ac_che.ms_mask[idx]= self.bits.get(1)
			#-decode_mid_side_stereo




	def decode_ics_info(self, _ics):
		if True:	#(m4ac.object_type != AOT_ER_AAC_ELD):
			if self.bits.get(1):	#reserved bit
				self.error= -3
				return

			_ics.windows_sequence[1]= _ics.windows_sequence[0]
			_ics.windows_sequence[0]= self.bits.get(2)
			_ics.is8= _ics.windows_sequence[0]==AACStatic.EIGHT_SHORT_SEQUENCE

			if False:	#(aot == AOT_ER_AAC_LD && _ics->window_sequence[0] != ONLY_LONG_SEQUENCE)
				None
				'''
				_ics.window_sequence[0] = AACStatic.ONLY_LONG_SEQUENCE
				self.error= -4
				return
				'''

			_ics.use_kb_window[1]= _ics.use_kb_window[0]
			_ics.use_kb_window[0]= self.bits.get(1)


		_ics.num_window_groups= 1
		_ics.group_len[0]= 1

		if _ics.is8:
			_ics.max_sfb= self.bits.get(4)
			
			for i in range(0,7):
				if self.bits.get(1):
					_ics.group_len[_ics.num_window_groups -1]+= 1
				else:
					_ics.num_window_groups+= 1;
					_ics.group_len[_ics.num_window_groups -1]= 1

			_ics.swb_offset= AACStatic.ff_swb_offset_128[self.ac_m4ac.sampling_index]
			_ics.num_swb= AACStatic.ff_aac_num_swb_128[self.ac_m4ac.sampling_index]
			_ics.tns_max_bands= AACStatic.ff_tns_max_bands_128[self.ac_m4ac.sampling_index]

			_ics.num_windows= 8
			_ics.predictor_present= 0

		else:
			_ics.num_windows= 1
			_ics.max_sfb= self.bits.get(6)

			if False:	#(aot == AOT_ER_AAC_LD || aot == AOT_ER_AAC_ELD)
				None
				'''
				if (m4ac->frame_length_short):
					_ics->swb_offset    =     ff_swb_offset_480[sampling_index];
					_ics->num_swb       =    ff_aac_num_swb_480[sampling_index];
					_ics->tns_max_bands =  ff_tns_max_bands_480[sampling_index];
				else:
					_ics->swb_offset    =     ff_swb_offset_512[sampling_index];
					_ics->num_swb       =    ff_aac_num_swb_512[sampling_index];
					_ics->tns_max_bands =  ff_tns_max_bands_512[sampling_index];

				if (!_ics->num_swb || !_ics->swb_offset)
					return AVERROR_BUG;
				'''
			else:
				_ics.swb_offset= AACStatic.ff_swb_offset_1024[self.ac_m4ac.sampling_index]
				_ics.num_swb= AACStatic.ff_aac_num_swb_1024[self.ac_m4ac.sampling_index]
				_ics.tns_max_bands= AACStatic.ff_tns_max_bands_1024[self.ac_m4ac.sampling_index]

			if True:	#(aot != AOT_ER_AAC_ELD)
				_ics.predictor_present= self.bits.get(1)
				_ics.predictor_reset_group= 0

			if _ics.predictor_present:	#not allowed
				if True:	#if (aot == AOT_AAC_LC || aot == AOT_ER_AAC_LC)
					self.error= -5
					return

				'''
				if (aot == AOT_AAC_MAIN)
					decode_prediction()
					
				else:
					if (aot == AOT_ER_AAC_LD):
						self.error= -5
						return

					_ics.ltp.present = self.bits.get(1)
					if _ics.ltp.present:
						decode_ltp(_ics)
				'''


		if _ics.max_sfb>_ics.num_swb: #scalefactor bands exceed limit
			self.error= -6
			return




	def decode_ics(self, _ics, _common_window):
		None




	'''
	decode provided packet, assumed being raw AAC
	'''
	def decodeAAC(self):

		#+decode_ics()
		global_gain= self.bits.get(8)


		#+decode_band_types
		band_type= [0]*120
		band_type_run_end= [0]*120

		idx= 0
		section_bits= 3 if packet_windows_sequence==2 else 5
		for g in range(0,ics.num_window_groups):
			k=0

			while k < ics.max_sfb:
				sect_end = k
				sect_band_type = self.bits.get(4)
				if sect_band_type == 12:	#invalid
					return -8

				while True:
					sect_len_incr= self.bits.get(section_bits)
					if not self.bits.left:	#underflow
						return -9

					sect_end += sect_len_incr
					if sect_end > ics.max_sfb:	#bands exceed limit
						return -10

					if sect_len_incr != (1<<section_bits) -1:
						break

				while k < sect_end:
					k+= 1
					band_type[idx] = sect_band_type
					band_type_run_end[idx] = sect_end
					idx+= 1
		#-decode_band_types


		#+decode_scalefactors
		offset= [global_gain, global_gain - 90, 0]
		sf= [0] *120
		idx= 0
		noise_flag= 1

		for g in range(0,ics.num_window_groups):
			for i in range(0,ics.max_sfb):
				run_end= band_type_run_end[idx]
				if band_type[idx] == 0:	#ZERO_BT
					while i<run_end:
						sf[idx]= 0.

						i+= 1
						idx+= 1

				elif band_type[idx] == 14 or band_type[idx] == 15:	#INTENSITY_BT, INTENSITY_BT2
					while i<run_end:
						offset[2]+= 0
						sf[idx]= 1

						i+= 1
						idx+= 1

				elif band_type[idx] == 13:	#NOISE_BT
					while i<run_end:
						noise_flag-= 1
						if noise_flag> 0:
							offset[1]+= self.bits.get(9) -256
						else:
							offset[1]+= 0

						i+= 1
						idx+= 1
				else:
					while i<run_end:
						offset[0]+= 0
						sf[idx]= 0.

						i+= 1
						idx+= 1

		#-decode_scalefactors


		pulse_present= self.bits.get(1)
		if pulse_present:
			if packet_windows_sequence==2:
				return -11

			#+decode_pulses
			num_pulse= self.bits.get(2) +1
			pulse_swb= self.bits.get(6)
			if pulse_swb>=ics.num_swb:
				return -12

			pos= [0,0,0,0]
			pos[0]= ics.swb_offset[pulse_swb] +self.bits.get(5)
			if pos[0]>1023:
				return -13

			amp= [0,0,0,0]
			amp[0]= self.bits.get(4)
			for i in range(1,num_pulse):
				pos[i]= self.bits.get(5) +pos[i-1]
				if pos[i]>1023:
					return -14
				amp[i]= self.bits.get(4)
			#-decode_pulses


		return self


		tns_present= self.bits.get(1)
		if tns_present:
		#+decode_tns	
			is8= packet_windows_sequence==2	#eight_short_seq
			tns_max_order= 7 if is8 else 12 #not AOT_AAC_MAIN, else 20

			for w in range(0,ics.num_windows):
				n_filt= self.bits.get(2 -is8)
				if n_filt:
					coef_res= self.bits.get(1)

					for filt in range(0,n_filt):
						length= self.bits.get(6 -2*is8)
						order= self.bits.get(5 -2*is8)
						if (order >tns_max_order):
							return -15

						if order:
							direction= self.bits.get(1)
							coeff_compress= self.bits.get(1)
							coef_len= 3+ coef_res -coeff_compress

							for i in range(0,order):
								self.bits.get(coef_len)
		#-decode_tns

		if self.bits.get(1):
			return -16

		#-decode_ics()







'''
0 8  s max_sfb 0 ms ms_mask                                       gain      
0 00 1 1010|00 0 01 111|11111111|11111111|11111111|01111111|11111 100|00001
101|0 01011 01|10 10000 1|000 00011| 0110 0001



simple
 
1A 08	0 00 1 1010|00 0 01 000
1A 0A	0 00 1 1010|00 0 01 010
1A 0B	0 00 1 1010|00 0 01 011
1A 0C	0 00 1 1010|00 0 01 100
1A 0D	0 00 1 1010|00 0 01 101
1A 0E	0 00 1 1010|00 0 01 110
1A 0F	0 00 1 1010|00 0 01 111

1A 13	0 00 1 1010|00 0 10 011
1A 14	0 00 1 1010|00 0 10 100
1A 15	0 00 1 1010|00 0 10 101
 

00 0E	0 00 0 0000|00 0 01 110
06 0F	0 00 0 0110|00 0 01 111
20 8E	0 01 0 0000|10 0 01 110
20 0A	0 01 0 0000|00 0 01 010
22 88	0 01 0 0010|10 0 01 000
4E 03	0 10 0 1110 | 0000001 1
4E 49	0 10 0 1110 | 0100100 1
4E 7A	0 10 0 1110 | 0111101 0
61 88	0 11 0 0001|10 0 01 000



complex


in
2A 0D	0 01 0 1010|00 0 01 101
2A 0E	0 01 0 1010|00 0 01 110
2A 0F	0 01 0 1010|00 0 01 111
2A 14	0 01 0 1010|00 0 10 100

mid
4C 36	0 10 0 1100 | 0011011 0
4C 37	0 10 0 1100 | 0011011 1
4C 6C	0 10 0 1100 | 0110110 0
4C 6D	0 10 0 1100 | 0110110 1
4C 9A	0 10 0 1100 | 1001101 0
4C C6	0 10 0 1100 | 1100011 0
4C CC	0 10 0 1100 | 1100110 0
4C D2	0 10 0 1100 | 1101001 0
4C D8	0 10 0 1100 | 1101100 0
4C D9	0 10 0 1100 | 1101110 1
4C DA	0 10 0 1100 | 1101101 0
4C DB	0 10 0 1100 | 1101101 1

out
7A 0D	0 11 1 1010|00 0 01 101
7A 0E	0 11 1 1010|00 0 01 110
7A 0F	0 11 1 1010|00 0 01 111
7A 14	0 11 1 1010|00 0 10 100



unique

20 05	0 01 0 0000|00 0 00 101
4C 6C	0 10 0 1100 | 01101100
7A 0F	0 11 1 1010|00 0 01 111

2A 0D	0 01 0 1010|00 0 01 101
67 CA	0 11 0 0111|11 0 01 010
4C 6C	0 10 0 1100 | 01101100
7A 14	0 11 1 1010|00 0 10 100
'''

