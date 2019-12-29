#!/usr/bin/env python3

import subprocess
import socket
import time

BUFSIZE = 1024
DEBUG = True

def readuntil(s,val,slow=False):
	buf = b''
	while not buf.endswith(val):
		if slow:
			ret = s.recv(1)
		else:
			ret = s.recv(BUFSIZE)
		buf = buf + ret
		if DEBUG and len(buf)%16 == 0:
			print(buf)
		#print(buf.decode('ascii'))
		if len(ret) == 0:
			break
			#raise Exception('received zero bytes')
	if DEBUG:
		print(buf)
	return buf

def sendall(s,buf):
	if DEBUG:
		print('>>', buf)
	n = s.send(buf)

def chal_exec(code):
	print("="*80)
	print(' '.join(['%02x'%x for x in code]))

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	#s.connect(('127.0.0.1',1215))
	s.connect(('3.93.128.89',1214))

	readuntil(s, b'Length of your Assemblium sequence: ').decode('ascii')
	sendall(s,b'%d\n'%len(code))
	readuntil(s, b'Enter your Assemblium sequence:\n').decode('ascii')
	#sendall(s,bytes(code)+b'\n')
	sendall(s,bytes(code))

	print(readuntil(s, b'FIN\n', True))#.decode('ascii'))

def write_to_stack(arr):
	# instructions to write this `arr` to stack
	arr = list(arr)
	new_arr = []
	for i in range(len(arr)):
		if arr[i] == 0:
			new_arr.append(0)
		elif arr[i] > 0 and arr[i] < 0x80:
			cnt = 0
			# write a value for each "bit" of the value
			for j in range(8):
				if arr[i]&(1<<j) != 0:
					new_arr.append(1<<j)
					cnt += 1
			# xor all the bits together
			new_arr = new_arr + [0x83]*(cnt-1)
			# this will save us the number of instructions / functions to implement
		elif arr[i]&0x80 == 0x80:
			new_arr.append(arr[i]^0x80)
			new_arr.append(0x80)
		else:
			raise Exception('should not hit this case %x' % arr[i])
			new_arr.append(arr[i])
	return new_arr

def write_to_output(arr):
	new_arr = []
	# instructions to write this `arr` to stack
	new_arr = new_arr + write_to_stack(reversed(arr))
	# now put each byte written to the stack to the outuput with 0xb0 instructions
	new_arr = new_arr + [0xb0]*len(arr)
	return new_arr

def create_function(inst_arr,id):
	inst_arr_rev = list(reversed(inst_arr))
	write_arr = write_to_stack([0xa1]+inst_arr_rev+[id]) + [0xa0]
	printa(write_arr)
	return write_arr

def printa(arr):
	print(' '.join('%02x'%x for x in arr))

if __name__ == '__main__':

	# create functions which write a byte to output and also add that byte to the stack
	f0 = create_function(write_to_output([0x00])+write_to_stack([0x40,0x80,0,0x80,0x30]),0)
	f1 = create_function(write_to_output([0x01])+write_to_stack([0x41,0x80,0,0x80,0x30]),1)
	f2 = create_function(write_to_output([0x02])+write_to_stack([0x42,0x80,0,0x80,0x30]),2)
	f3 = create_function(write_to_output([0x04])+write_to_stack([0x43,0x80,0,0x80,0x30]),3)
	f4 = create_function(write_to_output([0x08])+write_to_stack([0x44,0x80,0,0x80,0x30]),4)
	f5 = create_function(write_to_output([0x10])+write_to_stack([0x45,0x80,0,0x80,0x30]),5)
	f6 = create_function(write_to_output([0x20])+write_to_stack([0x46,0x80,0,0x80,0x30]),6)
	f7 = create_function(write_to_output([0x40])+write_to_stack([0x47,0x80,0,0x80,0x30]),7)
	f8 = create_function(write_to_output([0x80])+write_to_stack([0x48,0x80,0,0x80,0x30]),8)
	f9 = create_function(write_to_output([0x83])+write_to_stack([0x49,0x80,0,0x80,0x30]),9)
	f10 = create_function(write_to_output([0xa0])+write_to_stack([0x4a,0x80,0,0x80,0x30]),10)
	f11 = create_function(write_to_stack([0x4b,0x80,0,0x80,0x30])+[0,0xa0,0xc0,1,0xa0,0xc1],11)
	f12 = create_function(write_to_output([0x21])+write_to_stack([0x4c,0x80,0,0x80,0x30]),12)
	f13 = create_function(write_to_output([0x03])+write_to_stack([0x4d,0x80,0,0x80,0x30]),13)
	f14 = create_function(write_to_output([0x30])+write_to_stack([0x4e,0x80,0,0x80,0x30]),14)
	f15 = create_function(write_to_output([0x41])+write_to_stack([0x4f,0x80,0,0x80,0x30]),15)

	# Crib notes for what the last 5 actually mean
	printa([0x40,0x80,0,0x80,0x30])
	printa(write_to_stack([0xc0])+[0xb0])
	printa(reversed(write_to_stack([0xb0,0x80,0x40])))
	printa(reversed(write_to_stack(reversed(write_to_stack([0xc0])+[0xb0]))))

	# map instruction bytes to function calls
	lut = {}
	lut[0] = 0xc0
	lut[1] = 0xc1
	lut[2] = 0xc2
	lut[4] = 0xc3
	lut[8] = 0xc4
	lut[0x10] = 0xc5
	lut[0x20] = 0xc6
	lut[0x40] = 0xc7
	lut[0x80] = 0xc8
	lut[0x83] = 0xc9
	lut[0xa0] = 0xca
	lut[0x21] = 0xcc
	lut[0x03] = 0xcd
	lut[0x30] = 0xce
	lut[0x41] = 0xcf

	arr1 = f0+f1+f2+f3+f4+f5+f6+f7+f8+f9+f10+f11+f12+f13+f14+f15+write_to_stack([0xa1,0xa1])
	arr2 = []
	missing = {}
	for b in arr1:
		if b not in lut:
			missing[b] = None
		else:
			arr2.append(lut[b])
	print('missing:',[hex(x) for x in sorted(missing.keys())])

	chal_exec(arr1+arr2+[0xcb])


