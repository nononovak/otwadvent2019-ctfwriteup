#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import math

def do_plot(xr,yr,xg,yg):
	plt.plot(xr,yr, label='Red Light', color='red')
	plt.plot(xg,yg, label='Green Light', color='green')

	plt.xlabel('frame')
	plt.ylabel('luminecence')
	plt.title('Blinks')
	plt.legend()
	plt.show()

def normalize_color(yarr,val):
	yarr_new = []
	for y in yarr:
		if y > val:
			yarr_new.append(1)
		else:
			yarr_new.append(0)
	return yarr_new

if __name__ == '__main__':

	'''
	  ./video-morse-decode ../xGRTiTubviU.mkv aa.json 0 -1 0.71 0.14 0.76 0.21 > red_light.csv
	  ./video-morse-decode ../xGRTiTubviU.mkv aa.json 0 -1 0.33 0.24 0.38 0.32 > green_light.csv
	'''

	xr, yr = np.loadtxt('./video-morse-decode/red_light.csv', delimiter=',', unpack=True)
	xg, yg = np.loadtxt('./video-morse-decode/green_light.csv', delimiter=',', unpack=True)

	do_plot(xr,yr,xg,yg)
	i,j = 400,600
	do_plot(xr[i:j],yr[i:j],xg[i:j],yg[i:j])
	yr = normalize_color(yr,100)
	yg = normalize_color(yg,60)

	green_peaks = [i for i in range(1,len(xg)) if yg[i-1]==0 and yg[i]==1]

	all_bin = b''
	st = ''
	for i in range(len(green_peaks)-1):
		p1 = green_peaks[i]
		p2 = green_peaks[i+1]
		p2 = min(p1+6,p2)
		assert p2 >= p1+3
		val = sum(yr[p1:p2])/(p2-p1)
		#print(p1,val,round(val))
		st = st + '%d'%round(val)
		if green_peaks[i+1] > p1+10:
			print(len(st),len(st)%8,st)


			val = int(st,2)
			#val = val ^ ((1<<len(st))-1)
			bstr = val.to_bytes(len(st)//8,'big')
			print(val,bstr)
			all_bin = all_bin + bstr
			print('='*80, p1, green_peaks[i+1])
			st = ''

	print(all_bin)
