from .AACStatic import *
from .kiSupport import *


'''
AAC decoder suitable for AOT_AAC_LC L+R CPE.
Indeed it's a very bit of FFMPEG's aac_decode_frame_int(), shortcut where possible.
It's far from being a complete decoder and is made to detect Yi4k MP4's AAC.
'''
class AACCore():
	#Assumed audio properties, overriden by decodeADTS()
	crc_absent= 1
	num_aac_frames= 1;
	object_type= AACStatic.AOT_AAC_MAIN
	chan_config= 2	#(L+R)
	sampling_index= 3


	#runtimes
	sampling_rate= None
	samples= None


	#custom breakpoints
	restrictId= 0
	restrictType= AACStatic.TYPE_CPE


	#AAC decoded
	error= 0


	'''
	init AAC decoder for subsequental calls.
	Provided audio parameters will be overriden for ADTS frame
	'''
	def __init__ (self, samplingIndex=3, wantedId=0):	#(48000)
		self.sampling_index= samplingIndex
		self.sampling_rate= AACStatic.sample_rates[self.sampling_index]
		self.samples= self.num_aac_frames *1024

		self.restrictId= wantedId



	'''
	decode provided packet, assumed being ADTS
	'''
	def decodeADTS(self, _data):
		None

	'''
	decode provided packet, assumed being raw AAC
	'''
	def decodeAAC(self, _data):
		self.error= 0

		bits= Bits(_data)

		elem_type= bits.get(3)
		if self.restrictType>=0 and elem_type != self.restrictType:
			self.error= -1
			return self

		aac_id= bits.get(4)
		if self.restrictId>=0 and aac_id != self.restrictId:
			self.error= -2
			return self

		#+decode_cpe()
		common_window= bits.get(1)
		if not common_window:	#not used too
			self.error= -3
			return self

		#+decode_ics_info()
		if bits.get(1):	#reserved bit
			self.error= -4
			return self

		packet_windows_sequence= bits.get(2)
		packet_use_kb_window= bits.get(1)
		packet_group_len= 1
		num_window_groups= 1
		group_len= [1]+[0]*7

		if packet_windows_sequence==2: #eight_short_seq
			num_windows= 8
			predictor_present= 0

			max_sfb= bits.get(4)
			
			for i in range(0,7):
				if bits.get(1):
					group_len[num_window_groups -1]+= 1
				else:
					num_window_groups+= 1;
					group_len[num_window_groups -1]= 1

			
			swb_offset= AACStatic.ff_swb_offset_128[self.sampling_index]
			num_swb= AACStatic.ff_aac_num_swb_128[self.sampling_index]
			tns_max_bands= AACStatic.ff_tns_max_bands_128[self.sampling_index]

		else:
			num_windows= 1
			max_sfb= bits.get(6)

			swb_offset= AACStatic.ff_swb_offset_1024[self.sampling_index]
			num_swb= AACStatic.ff_aac_num_swb_1024[self.sampling_index]
			tns_max_bands= AACStatic.ff_tns_max_bands_1024[self.sampling_index]

			predictor_present= bits.get(1)
			if predictor_present:	#not allowed
				self.error= -5
				return self


		if max_sfb>num_swb: #scalefactor exceed limit
			self.error= -6
			return self

		#-decode_ics_info()


		ms_present= bits.get(2)
		if ms_present==3:	#reserved MS
			self.error= -7
			return self

		ms_mask= [0] *num_window_groups*max_sfb
		if ms_present==2:	#all 1
			ms_mask= [1] *num_window_groups*max_sfb

		if ms_present==1:
			for idx in range(0,num_window_groups*max_sfb):
				ms_mask[idx]= bits.get(1)


		#+decode_ics()
		global_gain= bits.get(8)


		band_type= [0]*120
		band_type_run_end= [0]*120

		idx= 0
		section_bits= 3 if packet_windows_sequence==2 else 5
		for g in range(0,num_window_groups):
			k=0

			while k < max_sfb:
				sect_end = k
				sect_band_type = bits.get(4)
				if sect_band_type == 12:	#invalid
					self.error= -8
					return self

				while True:
					sect_len_incr= bits.get(section_bits)
					if not bits.left:	#underflow
						self.error= -9
						return self

					sect_end += sect_len_incr
					if sect_end > max_sfb:	#bands exceed limit
						self.error= -10
						return self

					if sect_len_incr != (1<<section_bits) -1:
						break

				while k < sect_end:
					k+= 1
					band_type[idx] = sect_band_type
					band_type_run_end[idx] = sect_end
					idx+= 1

		return True


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

