#!/usr/bin/env python3

import struct
import sys

def read_bin(filename):
	f = open(filename,'rb')
	data = f.read()
	f.close()

	lines = []

	offset = 0
	while offset < len(data):
		label = data[offset:offset+4]
		if label == b'TiNy':
			offset += 4
			continue
		size, = struct.unpack('>I',data[offset+4:offset+8])
		content = data[offset+8:offset+8+size]

		if label == b'MeTa':
			pass
		elif label == b'TxTr':
			f = open(filename+'.%x'%offset+'.png','wb')
			f.write(content)
			f.close()
		elif label == b'LiNe':
			arr = [(content[i],content[i+1]) for i in range(0,len(content),2)]
			lines.append(arr)
		else:
			raise Exception('Unknown type', label)

		offset += 8+size

	return lines

def compute_lookup(filename='lines1.bin',linesname='lines1.txt',lookup={}):

	bin_lines = read_bin(filename)
	txt_lines = []
	for line in open(linesname):
		txt_lines.append(line.strip())

	arr1 = [len(x) for x in bin_lines]
	arr2 = [len(x) for x in txt_lines]
	assert arr1 == arr2

	for index1 in range(len(bin_lines)):
		for index2 in range(len(bin_lines[index1])):
			tup = bin_lines[index1][index2]
			ch = txt_lines[index1][index2]
			if lookup.get(tup,ch) != ch:
				raise Exception('lookup mismatch')
			lookup[tup] = ch

	return lookup

def solve_unknown(filename,lookup):

	bin_lines = read_bin(filename)

	for index1 in range(len(bin_lines)):
		st = ''
		for index2 in range(len(bin_lines[index1])):
			tup = bin_lines[index1][index2]
			st = st + lookup.get(tup,'[%d,%d]'%tup)
		print(st)


if __name__ == '__main__':

	lookup = {}
	lookup = compute_lookup('lines1.bin','lines1.txt',lookup)
	lookup = compute_lookup('lines2.bin','lines2.txt',lookup)
	lookup = compute_lookup('lines3.bin','lines3.txt',lookup)

	solve_unknown('lines4.bin',lookup)

	lookup[(1,9)] = '{'
	lookup[(7,9)] = '}'
	lookup[(5,6)] = 'c'
	lookup[(7,1)] = 'k'
	lookup[(5,3)] = '4'
	lookup[(2,2)] = '_'
	lookup[(2,0)] = '0'
	lookup[(1,5)] = '3'
	lookup[(3,8)] = '1'
	solve_unknown('lines4.bin',lookup)
