#!/usr/bin/env python

from __future__ import print_function
import midi
import sys

'''
   18  git clone https://github.com/vishnubob/python-midi
   19  cd python-midi/
   30  python setup.py install
'''

if __name__ == '__main__':
	music = midi.read_midifile('Stegno.mid')
	music.make_ticks_abs()
	#print(music)

	# note = midi.NoteOnEvent(tick=5280, channel=0, data=[67, 80])
	# note.tick, note.channel, data=[note.pitch, note.velocity]

	ticks_per_frame = 1920

	for track in music:
		notes = [note for note in track if note.name == 'Note On']
		pitch = [note.pitch for note in notes]
		tick = [note.tick for note in notes]
		#tracks += [tick, pitch]

	#print music[0][0]
	#treble_track = music[0]

	arr = []
	pitch_lookup = {}
	pitch_lookup[79] = '0' # G
	pitch_lookup[76] = '5' # E
	pitch_lookup[74] = '4' # D
	pitch_lookup[72] = '3' # C
	pitch_lookup[71] = '2' # B
	pitch_lookup[69] = '1' # A
	pitch_lookup[67] = '0' # G
	pitch_lookup[66] = '6' # F#
	pitch_lookup[64] = '5' # E
	pitch_lookup[62] = '4' # D

	pitch_lookup[47] = '2' # B
	pitch_lookup[45] = '1' # A
	pitch_lookup[43] = '0' # G
	pitch_lookup[42] = '6' # F#
	pitch_lookup[40] = '5' # E
	pitch_lookup[38] = '4' # D
	pitch_lookup[36] = '3' # C
	pitch_lookup[35] = '2' # B
	pitch_lookup[28] = '5' # E

	notes_on = {}
	for note in music[0]: # Treble track
		if note.name != 'Note On':
			continue
		pitch = note.pitch
		tick = note.tick
		if note.velocity > 0: # pressed
			notes_on[pitch] = tick
		else:
			ptick = notes_on[pitch]
			del(notes_on[pitch])
			#print(pitch, (1.*ptick/ticks_per_frame,1.*tick/ticks_per_frame))
			arr.append((1.*ptick/ticks_per_frame,1.*tick/ticks_per_frame,pitch))

	notes_on = {}
	for note in music[1]: # Treble track
		if note.name != 'Note On':
			continue
		pitch = note.pitch
		tick = note.tick
		if note.velocity > 0: # pressed
			notes_on[pitch] = tick
		else:
			ptick = notes_on[pitch]
			del(notes_on[pitch])
			#print(pitch, (1.*ptick/ticks_per_frame,1.*tick/ticks_per_frame))
			arr.append((1.*ptick/ticks_per_frame,1.*tick/ticks_per_frame,pitch))

	arr.sort()
	for (t0,t1,pitch) in arr:
		notes = [p for (_t0,_t1,p) in arr if _t0 <= t0 and t0 < _t1]
		notes.sort()
		#print(t0, ''.join(pitch_lookup[p] for p in notes), notes)

	times = []

	'''
	# Look at the four 8-measure matches side-by-side
	for t in range(0,8*16):
		t0 = 1.*t/16
		notes1 = [p for (_t0,_t1,p) in arr if _t0 <= t0 and t0 < _t1]
		notes2 = [p for (_t0,_t1,p) in arr if _t0 <= t0+8 and t0+8 < _t1]
		notes3 = [p for (_t0,_t1,p) in arr if _t0 <= t0+40 and t0+40 < _t1]
		notes4 = [p for (_t0,_t1,p) in arr if _t0 <= t0+48 and t0+48 < _t1]
		notes1.sort()
		notes2.sort()
		notes3.sort()
		notes4.sort()
		bnotes1 = ''.join(pitch_lookup[p] for p in sorted(notes1))
		bnotes2 = ''.join(pitch_lookup[p] for p in sorted(notes2))
		bnotes3 = ''.join(pitch_lookup[p] for p in sorted(notes3))
		bnotes4 = ''.join(pitch_lookup[p] for p in sorted(notes4))
		print('%.4f'%t0, '%-4s'%bnotes1, '%-4s'%bnotes2, '%-4s'%bnotes3, '%-4s'%bnotes4, '%-10s'%(notes1 == notes3), '%-10s'%(notes2 == notes4), '%-20s'%notes1, '%-20s'%notes2, '%-20s'%notes3, '%-20s'%notes4)

	sys.exit(0)
	#'''

	'''
	# Look at 40 measures side-by-side
	for t in range(0,40*16-1):
		if t%16 == 0:
			print('='*100)
		t0 = 1.*t/16
		t1 = 1.*(t+1)/16
		notes1 = [p for (_t0,_t1,p) in arr if _t0 <= t0 and t0 < _t1]
		notes1b = [p for (_t0,_t1,p) in arr if _t0 <= t1 and t1 < _t1]
		notes2 = [p for (_t0,_t1,p) in arr if _t0 <= t0+40 and t0+40 < _t1]
		notes1.sort()
		notes2.sort()
		bnotes1 = ''.join(pitch_lookup[p] for p in sorted(notes1))
		bnotes2 = ''.join(pitch_lookup[p] for p in sorted(notes2))
		print('%.4f'%t0, '%-4s'%bnotes1, '%-4s'%bnotes2, '%-10s'%(notes1 == notes2), '%-20s'%notes1, '%-20s'%notes2)

	sys.exit(0)
	#'''

	ans = ''
	for t in range(0,80*16,2):
		if t%16 == 0:
			print('='*100)
		t0 = 1.*t/16
		t1 = 1.*(t+1)/16
		notes1 = [p for (_t0,_t1,p) in arr if _t0 <= t0 and t0 < _t1]
		notes2 = [p for (_t0,_t1,p) in arr if _t0 <= t1 and t1 < _t1]
		notes1.sort()
		notes2.sort()
		bnotes1 = ''.join(pitch_lookup[p] for p in sorted(notes1))
		bnotes2 = ''.join(pitch_lookup[p] for p in sorted(notes2))
		ch = ''
		if notes1 != notes2 and len(notes1) == len(notes2):
			for i in range(len(bnotes1)):
				if bnotes1[i] != bnotes2[i]:
					ch = bnotes2[i]
		print('%.4f'%t0, '%-4s'%bnotes1, '%-4s'%bnotes2, '%-10s'%(notes1 == notes2), '%-20s'%notes1, '%-20s'%notes2, ch, [chr(int(ans[i:i+3],7)) for i in range(0,len(ans),3)])
		ans = ans + ch
	print(ans, len(ans))
	print([chr(int(ans[i:i+3],7)) for i in range(0,len(ans),3)])
	ans2 = ans[:-5]+'1'+ans[-5:]
	print([chr(int(ans2[i:i+3],7)) for i in range(0,len(ans2),3)])


# AOTW{ ... }
# A = 122 b7
# O = 142 b7
# T = 150 b7
# W = 153 b7
# { = 234 b7
# _ = 165 b7
# } = 236 b7

# BABAG, D, AABAG, E, 
# 79 G
# 76 E
# 74 D
# 72 C
# 71 B
# 69 A
# 67 G
# 66 F#
# 64 E
# 62 D

# Bass
# EG/B, DF/A, ., C/GE, EG/B
# 47 B
# 45 A
# 43 G
# 42 F#
# 40 E
# 38 D
# 36 C
# 35 B
# 28 E
