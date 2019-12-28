#!/usr/bin/env python3

import numpy as np
import struct

if __name__ == '__main__':

	'''
	(x0,x1,x2,x3) = (0,0,0,1)
	for i in range(20):
		print(i, x0,x1,x2,x3)
		y0 = x0*16 + x1*15 + x2*14 + x3*13
		y1 = x0*12 + x1*11 + x2*10 + x3* 9
		y2 = x0* 8 + x1* 7 + x2* 6 + x3* 5
		y3 = x0* 4 + x1* 3 + x2* 2 + x3* 1
		x0 = y0 % 0x0096433D
		x1 = y1 % 0x0096433D
		x2 = y2 % 0x0096433D
		x3 = y3 % 0x0096433D
		'''

	N = 1234567890123456789

	m = np.matrix([[16,15,14,13],[12,11,10,9],[8,7,6,5],[4,3,2,1]])

	N_bits = []
	while N > 0:
		N_bits.append(N&1)
		N = N>>1
	N_bits.reverse()

	p = m
	for i in N_bits[1:]:
		p = (p*p) % 0x0096433D
		if i == 1:
			p = (p*m) % 0x0096433D

	xmm0 = (p.item(0,3)<<0) | (p.item(0,2)<<32) | (p.item(0,1)<<64) | (p.item(0,0)<<96)
	xmm1 = (p.item(1,3)<<0) | (p.item(1,2)<<32) | (p.item(1,1)<<64) | (p.item(1,0)<<96)
	xmm2 = (p.item(2,3)<<0) | (p.item(2,2)<<32) | (p.item(2,1)<<64) | (p.item(2,0)<<96)
	xmm3 = (p.item(3,3)<<0) | (p.item(3,2)<<32) | (p.item(3,1)<<64) | (p.item(3,0)<<96)

	f = open('326c15f8884fcc13d18a60e2fb933b0e35060efa8a44214e06d589e4e235fe34','rb').read()[0x00001090:0x000010b0]

	res = int.to_bytes(xmm3,16,'little') + int.to_bytes(xmm2,16,'little') + int.to_bytes(xmm1,16,'little') + int.to_bytes(xmm0,16,'little')
	ans = b''
	for i in range(0,32,2):
		ans = ans + bytes([res[2*i+0]^f[i],res[2*i+1]^f[i+1]])
	print(ans)
