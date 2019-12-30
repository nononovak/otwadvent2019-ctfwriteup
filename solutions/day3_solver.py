#!/usr/bin/env python3

import binascii
import struct

if __name__ == '__main__':
	data = open('bitstream.dat','rb').read()
	#print(len(data))

	index = 0x180
	bitstream = [1]
	while index < 0x8c617d:#len(data):
		next_index = int(index + 2*(100000/2400.))
		next_index_a = next_index
		while data[next_index_a] == 1:
			next_index_a -= 1
		next_index_b = next_index
		while data[next_index_b] == 1:
			next_index_b += 1
		next_index = (next_index_a+next_index_b)/2

		vals = data[int(index):int(next_index)]
		n0 = vals.count(b'\x00')
		n1 = vals.count(b'\x01')
		x = (n0-n1)*2
		if x > ((n0+n1)/2):
			# bit is 0
			bit = 0
		else:
			bit = 1
		bitstream.append(bit)
		#print(hex(int(index)), n0, n1, bit)
		index = next_index

	for start in range(8):
		bytestream = []
		for index in range(start,len(bitstream)-8,8):
			bytestream.append(sum([bitstream[index+i]<<(7-i) for i in range(8)]))
		f = open('output%d.bin'%start, 'wb')
		f.write(bytes(bytestream))
		f.close()

	bitstream = bitstream

	bytestream0 = []
	for index in range(0,len(bitstream)-8,8):
		bytestream0.append(sum([bitstream[index+i]<<(7-i) for i in range(8)]))

	bytestream0 = bytes(bytestream0)

	bestN = 8

	for index in range(0,len(bytestream0), 0x152):
	#for index in range(0,bestN*0x152, 0x152):
		print('0x%04x'%index, binascii.hexlify(bytestream0[index:index+0x152]))


	new_bitstream = []
	for i in range(8*0x152):
		c0 = bitstream[i:bestN*8*0x152:8*0x152].count(0)
		c1 = bitstream[i:bestN*8*0x152:8*0x152].count(1)
		#print(bitstream[i:bestN*8*0x152:8*0x152], c0, c1)
		if c0 > c1:
			new_bitstream.append(0)
		else:
			new_bitstream.append(1)

	bytestream0 = []
	for index in range(0,len(new_bitstream),8):
		bytestream0.append(sum([new_bitstream[index+i]<<(7-i) for i in range(8)]))

	bytestream0 = bytes(bytestream0)

	print('XXXXXX', binascii.hexlify(bytestream0))

	for index in range(0,len(bytestream0),13):
		print(binascii.hexlify(bytestream0[index:index+13]), bytestream0[index:index+13])

	# https://en.wikipedia.org/wiki/Radio_Data_System
	new_bitstream = [b^1 for b in new_bitstream]
	for index in range(0,len(new_bitstream),104):
		pi_code = sum([new_bitstream[index+i]<<(15-i) for i in range(16)])
		gi_type = sum([new_bitstream[index+26+i]<<(15-i) for i in range(16)])
		char_ab = sum([new_bitstream[index+2*26+i]<<(15-i) for i in range(16)])
		char_cd = sum([new_bitstream[index+3*26+i]<<(15-i) for i in range(16)])

		print(hex(pi_code), hex(gi_type), hex(char_ab), hex(char_cd), struct.pack('>H',char_ab), struct.pack('>H',char_cd))

	print(binascii.unhexlify('7370726561645f584d41535f63683333723a5f7331'))
