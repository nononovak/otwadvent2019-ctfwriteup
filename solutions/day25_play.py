#!/usr/bin/env python3

import socket
import sys
import binascii
import re
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

def readall(s,val,slow=False):
	buf = b''

SENT_BUFFER = b''

def sendall(s,buf):
	global SENT_BUFFER
	if DEBUG:
		print('>>', buf)
	SENT_BUFFER = SENT_BUFFER + buf
	s.send(buf)

def chunk_ansi(data):
	arr = []
	last_end = 0
	pat = re.compile('\x1b\[([0-9;]*)(\w)')
	#print('>>', data.encode('utf-8'), flush=True)
	#print(data)
	for match in re.finditer(pat,data):
		#print(match,match.group(1),match.group(2))
		start = match.start()
		end = match.end()
		if last_end != start:
			arr.append(data[last_end:start])
		if match.group(2) == 'H':
			arr.append(tuple(int(x) for x in match.group(1).split(';')))
		last_end = end
	if last_end != len(data):
		arr.append(data[last_end:])
	#print('<<', arr)
	return arr

def text_from_ansi(arr):
	return ''.join([x for x in arr if type(x) == str])

# https://stackoverflow.com/questions/510357/python-read-a-single-character-from-the-user
def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

def get_grid(st):
	lines = st.strip().split('\n')
	grid = {}
	for y,line in enumerate(lines[-14:]):
		line = line[-18:]
		for x,ch in enumerate(line[-18:]):
			grid[x,y] = ch
	return '\n'.join(line[-18:] for line in lines[-14:]), grid

GLOBAL_GRID = defaultdict(lambda:'?')

def extract_grid_pieces(grid):
	# TODO track global grid
	#print(grid)
	global GLOBAL_GRID
	center = grid[9,6]
	pos_x = int(grid[7,11]+grid[8,11])
	pos_y = int(grid[10,11]+grid[11,11])
	print('grid data:', center, pos_x, pos_y)
	for i in range(2,16):
		x = i-9+pos_x
		for j in range(3,10):
			y = j-6+pos_y
			if (x,y) != (pos_x,pos_y):
				GLOBAL_GRID[x,y] = grid[i,j]

	if pos_x >= 80 and pos_y >= 80:
		global DEBUG
		DEBUG = True

	return (center,pos_x,pos_y)

def print_global_grid(center,x_pos,y_pos):
	global GLOBAL_GRID
	st = ''
	for y in range(0,84//2):
		for x in range(0,83):
			if (x,y) == (x_pos,y_pos):
				st = st + center
			else:
				st = st + GLOBAL_GRID[x,y]
		y = y + (84//2)
		st = st + '   '
		for x in range(0,83):
			if (x,y) == (x_pos,y_pos):
				st = st + center
			else:
				st = st + GLOBAL_GRID[x,y]
		st = st + '\n'
	print(st)

def read_game(s):
	ret = readuntil(s,b'+----------------+\x1b[0m\n')
	while b'end:' not in ret:
		ret = ret + readuntil(s,b'+----------------+\x1b[0m\n')
	display = text_from_ansi(chunk_ansi(ret.decode('utf-8')))
	print(display)
	grid_display,grid = get_grid(display)
	#print(grid_display)
	(center,pos_x,pos_y) = extract_grid_pieces(grid)
	print_global_grid(center,pos_x,pos_y)
	return (display, grid_display, grid)

def play():

	getch = _find_getch()

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	s.connect(('3.93.128.89',1225))

	readuntil(s,b'width: ')
	#sendall(s,b'211\n')
	sendall(s,b'100\n')
	readuntil(s,b'height: ')
	#sendall(s,b'57\n')
	sendall(s,b'40\n')

	(display, grid_display, grid) = read_game(s)

	did_twiddle = False

	while True:

		#print(SENT_BUFFER)
		b = getch()
		print('char was', repr(b))
		if ord(b) < 10:
			# ctrl-C
			break

		if b == 'w' or b == 's':
			#b = b * 4
			(c, x, y) = extract_grid_pieces(grid)
			pos_x,pos_y = x,y
			count = 0
			while (x,y) == (pos_x,pos_y) and count < 10:
				print('going', b, (c,x,y), (pos_x,pos_y))
				sendall(s,b.encode('ascii'))
				(display, grid_display, grid) = read_game(s)
				(c, x, y) = extract_grid_pieces(grid)
				count += 1
			if count >= 10:
				if not did_twiddle:
					sendall(s,b'd')
				else:
					sendall(s,b'a')
				did_twiddle = not did_twiddle
				(display, grid_display, grid) = read_game(s)
				(c, x, y) = extract_grid_pieces(grid)
				count = 0
				while (x,y) == (pos_x,pos_y) and count < 10:
					print('going', b, (c,x,y), (pos_x,pos_y))
					sendall(s,b.encode('ascii'))
					(display, grid_display, grid) = read_game(s)
					(c, x, y) = extract_grid_pieces(grid)
					count += 1
			print('finished loop', b, (c,x,y), (pos_x,pos_y))
			sendall(s,b.encode('ascii'))
			(display, grid_display, grid) = read_game(s)

		elif b == 'd' or b == 'a':
			#b = b * 6
			did_twiddle = False
			nav_h = {}
			# v --> 1/2 for [0,5] left to right
			# < --> 1 for [0,5] left to right
			# ^ --> 2 for [0,4] left to right
			# > --> 4 for [0,8] left to right
			nav_h['d','^'] = '>',3
			nav_h['d','>'] = 'v',1
			nav_h['d','v'] = '<',1
			nav_h['d','<'] = '^',1
			nav_h['a','^'] = '<',1
			nav_h['a','>'] = '^',1
			nav_h['a','v'] = '>',3
			nav_h['a','<'] = 'v',1

			(c, x, y) = extract_grid_pieces(grid)
			target_direction,extra_count = nav_h[b,c]
			while c != target_direction:
				print('going', 'd', (c,x,y))
				sendall(s,b'd')
				(display, grid_display, grid) = read_game(s)
				(c, x, y) = extract_grid_pieces(grid)

			for i in range(extra_count):
				print('going', 'd', (c,x,y))
				sendall(s,b'd')
				(display, grid_display, grid) = read_game(s)
				(c, x, y) = extract_grid_pieces(grid)

		elif b == 'd' or b == 'a':
			(c, x, y) = extract_grid_pieces(grid)
			center = c
			count = 0
			while (c) == (center) and count < 10:
				print('going', b, (c,x,y), center)
				sendall(s,b.encode('ascii'))
				(display, grid_display, grid) = read_game(s)
				(c, x, y) = extract_grid_pieces(grid)
				count += 1
			print('finished loop', b, (c,x,y), (pos_x,pos_y))
			sendall(s,b.encode('ascii'))
			(display, grid_display, grid) = read_game(s)
			sendall(s,b.encode('ascii'))
			(display, grid_display, grid) = read_game(s)

		else:
			sendall(s,b.encode('ascii'))
			(display, grid_display, grid) = read_game(s)

		sendall(s,b' ')
		(display, grid_display, grid) = read_game(s)

if __name__ == '__main__':

	play()
