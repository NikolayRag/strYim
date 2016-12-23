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
	error= None


	limitSequence= None
	limitOnce= None


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
	def aac_decode_frame(self, _data, limitOnce=True, limitSequence=-1):
		self.limitSequence= limitSequence
		self.limitOnce= limitOnce

		self.bits= Bits(_data)
		self.error= 0

		self.ac_m4ac= MPEG4AudioConfig(self.m4ac)


		#aac_decode_frame_int() inlined

#  todo 178 (feature) -1: read ADTS header, bitstream seek() must be implemented
#		if self.bits.get(12) == 0xfff:
#			self.readADTS(self.ac_m4ac)
#		else:
#			self.bits.seek(0)


		#other profiles not supported (yet?)
		if (
			self.ac_m4ac.object_type != AACStatic.AOT_AAC_LC
		):
			self.error= -1
			return self


		while True:
			elem_type= self.bits.get(3)
			if elem_type==AACStatic.TYPE_END:
				break

			aac_id= self.bits.get(4)

			self.ac_che= ChannelElement()
			self.sce_ics0= SCE_ICS()


			#TYPE_CPE is only one supported indeed
#  todo 182 (feature, aac) -1: add different aac types
			if elem_type == AACStatic.TYPE_CPE:
				self.decode_cpe()

			else:
				self.error= -2


			if self.error:
				break
#  todo 181 (feature, aac, clean) +0: remove after full decoding done
			if self.limitOnce or 1: #only one AAC block atm, sorry
				break


		return self



	


	def decode_cpe(self):
		ics= self.sce_ics0

		self.ac_che.common_window= self.bits.get(1)

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


			self.ac_che.ms_present= self.bits.get(2)
			if self.ac_che.ms_present==3:	#reserved MS
				self.error= -11
				return

			#+decode_mid_side_stereo
			if self.ac_che.ms_present==2:	#all 1
				self.ac_che.ms_mask= [1] *ics.num_window_groups*ics.max_sfb

			if self.ac_che.ms_present==1:
				for idx in range(0,ics.num_window_groups*ics.max_sfb):
					self.ac_che.ms_mask[idx]= self.bits.get(1)
			#-decode_mid_side_stereo


		self.decode_ics(ics)
		if self.error:
			return




	def decode_ics_info(self, _ics):
		if True:	#(m4ac.object_type != AOT_ER_AAC_ELD):
			if self.bits.get(1):	#reserved bit
				self.error= -21
				return

			_ics.windows_sequence[1]= _ics.windows_sequence[0]
			_ics.windows_sequence[0]= self.bits.get(2)
			_ics.is8= _ics.windows_sequence[0]==AACStatic.EIGHT_SHORT_SEQUENCE

			if self.limitSequence!=-1:
				if _ics.windows_sequence[0]>1 != self.limitSequence:	#short/long sequence switching order
					self.error= -22
					return


			if False:	#(aot == AOT_ER_AAC_LD && _ics->window_sequence[0] != ONLY_LONG_SEQUENCE)
				None
				'''
				_ics.window_sequence[0] = AACStatic.ONLY_LONG_SEQUENCE
				self.error= 23
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
					self.error= -24
					return

				'''
				if (aot == AOT_AAC_MAIN)
					decode_prediction()
					
				else:
					if (aot == AOT_ER_AAC_LD):
						self.error= -25
						return

					_ics.ltp.present = self.bits.get(1)
					if _ics.ltp.present:
						decode_ltp(_ics)
				'''


		if _ics.max_sfb>_ics.num_swb: #scalefactor bands exceed limit
			self.error= -26
			return




	def decode_ics(self, _ics):
		global_gain= self.bits.get(8)


		if False:	#!common_window && !scale_flag
			None
			'''
			decode_ics_info(_ics)
			if self.error:
				self.error= -31
				return
			'''


		#+decode_band_types()
		idx= 0
		bits= 3 if _ics.is8 else 5
		bitsMax= 0b111 if _ics.is8 else 0b11111
		for g in range(0,_ics.num_window_groups):
			k=0
			while k < _ics.max_sfb:
				sect_end = k
				sect_band_type = self.bits.get(4)
				if sect_band_type == AACStatic.RESERVED_BT:
					self.error= -32
					return

				while True:
					sect_len_incr= self.bits.get(bits)
					if not self.bits.left:	#underflow
						self.error= -33
						return

					sect_end += sect_len_incr
					if sect_end > _ics.max_sfb:	#bands exceed limit
						self.error= -34
						return

					if sect_len_incr != bitsMax:
						break

				while k < sect_end:
					_ics.band_type[idx] = sect_band_type
					_ics.band_type_run_end[idx] = sect_end
					idx+= 1

					k+= 1
		#-decode_band_types()


		return


#!!!! DANGER !!!!
#no road beyond this point
#!!!! DANGER !!!!


		#+decode_scalefactors()
		idx= 0
		offset= [global_gain, global_gain-AACStatic.NOISE_OFFSET, 0]
		noise_flag= True

		for g in range(0,_ics.num_window_groups):
			for i in range(0,_ics.max_sfb):
				run_end= _ics.band_type_run_end[idx]
				if _ics.band_type[idx] == AACStatic.ZERO_BT:
					while i<run_end:
						_ics.sf[idx]= 0

						i+= 1
						idx+= 1

				elif _ics.band_type[idx] == AACStatic.INTENSITY_BT or _ics.band_type[idx] == AACStatic.INTENSITY_BT2:
					while i<run_end:
						offset[2]+= self.get_vlc2() -AACStatic.SCALE_DIFF_ZERO
						_ics.sf[idx]= 100 -clip(offset[2], -155, 100)

						i+= 1
						idx+= 1

				elif _ics.band_type[idx] == AACStatic.NOISE_BT:
					while i<run_end:
						if noise_flag:
							offset[1]+= self.bits.get(AACStatic.NOISE_PRE_BITS) -AACStatic.NOISE_PRE
							noise_flag= False
						else:
							offset[1]+= self.get_vlc2() -AACStatic.SCALE_DIFF_ZERO

						_ics.sf[idx]= -clip(offset[1], -100, 155)

						i+= 1
						idx+= 1
				else:
					while i<run_end:
						offset[0]+= self.get_vlc2() -AACStatic.SCALE_DIFF_ZERO
						if offset[0]>255:
							self.error= -35
							return

						_ics.sf[idx]= -offset[0]

						i+= 1
						idx+= 1

		#-decode_scalefactors()


		out= _ics.coeffs
		pulse= Pulse()
		pulse_present= 0
		eld_syntax= False	#ac_m4ac.object_type == AOT_ER_AAC_ELD
		er_syntax= False	#ac_m4ac.object_type == AOT_ER_AAC_LC || AOT_ER_AAC_LTP || AOT_ER_AAC_LD || AOT_ER_AAC_ELD




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





	def get_vlc2(self): #precoded bits=7, depth=3
		None
