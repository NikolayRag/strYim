from .kiSupport import *


'''
AAC decoder suitable for AOT_AAC_LC L+R CPE.
Indeed it's a very bit of FFMPEG's aac_decode_frame_int(), shortcut where possible.
It's far from being a complete decoder and is made to detect Yi4k MP4's AAC.
'''
class AACCore():
	sample_ratesA= [96000, 88200, 64000, 48000, 44100, 32000, 24000, 22050, 16000, 12000, 11025, 8000, 7350]
	ff_aac_num_swb_128= [12, 12, 12, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15]
	ff_tns_max_bands_128= [9, 9, 10, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14]
	ff_swb_offset_128= [
		0,
		0,
		0,
		[0, 4, 8, 12, 16, 20, 28, 36, 44, 56, 68, 80, 96, 112, 128]
	]

	ff_aac_num_swb_1024= [41, 41, 47, 49, 49, 51, 47, 47, 43, 43, 43, 40, 40]
	ff_tns_max_bands_1024= [31, 31, 34, 40, 42, 51, 46, 46, 42, 42, 42, 39, 39]
	ff_swb_offset_1024= [
		0,
		0,
		0,
		[0,   4,   8,  12,  16,  20,  24,  28, 32,  36,  40,  48,  56,  64,  72,  80, 88,  96, 108, 120, 132, 144, 160, 176, 196, 216, 240, 264, 292, 320, 352, 384, 416, 448, 480, 512, 544, 576, 608, 640, 672, 704, 736, 768, 800, 832, 864, 896, 928, 1024]
	]

	crc_absent= 1
	num_aac_frames= 1;
	object_type=2	#(AOT_AAC_LC)
	chan_config=2	#(L+R)
	samples= num_aac_frames *1024;

	sampling_index=3	#(48000)
	sampling_rate=None

	pos=None	#[byte,bit] position


	def __init__ (self, sampling_index=3):
		self.sampling_index= sampling_index
		self.sampling_rate= self.sample_ratesA[self.sampling_index]


	'''
	decode provided packet, assumed being ADTS
	'''
	def decodeADTS(self, _data):
		None

	'''
	decode provided packet, assumed being raw AAC
	'''
	def decodeAAC(self, _data, _offset=0):
		self.pos= [_offset,0]
		elem_type= bitsGet(_data, 3, self.pos)
		if elem_type !=1:	#only CPE so far
			return -1

		aac_id= bitsGet(_data, 4, self.pos)
		if aac_id>0:	#didnt saw other, used to tighten detection
			return -2

		#+decode_cpe()
		common_window= bitsGet(_data, 1, self.pos)
		if not common_window:	#not used too
			return -3

		#+decode_ics_info()
		if bitsGet(_data, 1, self.pos):	#reserved bit
			return -4

		packet_windows_sequence= bitsGet(_data, 2, self.pos)
		packet_use_kb_window= bitsGet(_data, 1, self.pos)
		packet_group_len= 1
		num_window_groups= 1
		group_len= [1]+[0]*7

		if packet_windows_sequence==2: #eight_short_seq
			num_windows= 8
			predictor_present= 0

			max_sfb= bitsGet(_data, 4, self.pos)
			
			for i in range(0,7):
				if bitsGet(_data, 1, self.pos):
					group_len[num_window_groups -1]+= 1
				else:
					num_window_groups+= 1;
					group_len[num_window_groups -1]= 1

			
			swb_offset= self.ff_swb_offset_128[self.sampling_index]
			num_swb= self.ff_aac_num_swb_128[self.sampling_index]
			tns_max_bands= self.ff_tns_max_bands_128[self.sampling_index]

		else:
			num_windows= 1
			max_sfb= bitsGet(_data, 6, self.pos)

			swb_offset= self.ff_swb_offset_1024[self.sampling_index]
			num_swb= self.ff_aac_num_swb_1024[self.sampling_index]
			tns_max_bands= self.ff_tns_max_bands_1024[self.sampling_index]

			predictor_present= bitsGet(_data, 1, self.pos)
			if predictor_present:	#not allowed
				return -5


		if max_sfb>num_swb: #scalefactor exceed limit
			return -6

		#-decode_ics_info()


		ms_present= bitsGet(_data, 2, self.pos)
		if ms_present==3:	#reserved MS
			return -7

		ms_mask= [0] *num_window_groups*max_sfb
		if ms_present==2:	#all 1
			ms_mask= [1] *num_window_groups*max_sfb

		if ms_present==1:
			for idx in range(0,num_window_groups*max_sfb):
				ms_mask[idx]= bitsGet(_data, 1, self.pos)


		#+decode_ics()
		global_gain= bitsGet(_data, 8, self.pos)


		band_type= [0]*120
		band_type_run_end= [0]*120

		idx= 0
		section_bits= 3 if packet_windows_sequence==2 else 5
		for g in range(0,num_window_groups):
			k=0

			while k < max_sfb:
				sect_end = k
				sect_band_type = bitsGet(_data, 4, self.pos)
				if sect_band_type == 12:	#invalid
					return -8

				while True:
					sect_len_incr= bitsGet(_data, section_bits, self.pos)
					if self.pos>len(_data):
						return -9

					sect_end += sect_len_incr
					if sect_end > max_sfb:	#bands exceed limit
						return -10

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

