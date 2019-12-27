#!/usr/bin/env python3

# ./solver.py | nc 3.93.128.89 1218

import sys

def sqrt_pow32(n):
	norig = n
	if n == 0:
		return []
	mult = 1
	while n % 4 == 0:
		n = n // 4
		mult *= 2
	if n%8 != 1:
		return []
	arr = [1,3,5,7]
	for powi in range(3,32):
		#print(hex(n),powi,arr)
		new_arr = []
		for a in arr:
			for anew in [a,a+2**powi]:
				if (anew**2) % 2**(powi+1) == n % 2**(powi+1):
					new_arr.append(anew)
		arr = new_arr
	new_arr = []
	for a in arr:
		x = mult*a % 2**32
		if (x)**2 % 2**32 == norig and x not in new_arr:
			new_arr.append(x)
	return new_arr

def solve_row(arr):

	#arr = arr + [1]*(7-len(arr))
	#print(arr)
	s = sum(arr) % 2**32
	p = 1
	for x in arr:
		p *= x
	p = p%2**32

	s0 = s
	p0 = p

	#print('sum:', s0, hex(s))
	#print('prod:', p0, hex(p))

	# X + Y + S == 45
	# X * Y * P == 362880

	s1 = (2**32+45-s0) % 2**32

	# Y = S1 - X
	# X * (S1 - X) * P == 362880
	# 0 == P * X**2 + (-S1 * P) * X + 362880
	#print('0 == %d * X**2 + %d * X + %d' % (p, (-s1*p)%2**32, 362880))
	#print('0 == 0x%x * X**2 + 0x%x * X + 0x%x' % (p, (-s1*p)%2**32, 362880))

	x2 = (p)%2**32
	x1 = (-s1*p)%2**32
	x0 = (362880)%2**32

	while (x2%2) == 0 and (x1%2) == 0 and (x0%2) == 0:
		x2 = x2//2
		x1 = x1//2
		x0 = x0//2

	if x2 & 1 == 1:
		pinv = pow(x2,(2**31)-1,2**32)
		x2 = (x2*pinv)%2**32
		x1 = (x1*pinv)%2**32
		x0 = (x0*pinv)%2**32

		#pinv = pow(p,(2**31)-1,2**32)
		#x2 = (p*pinv)%2**32
		#x1 = (-s1*p*pinv)%2**32
		#x0 = (362880*pinv)%2**32
		#print('0 == %d * X**2 + %d * X + %d' % (x2, x1, x0))
		#print('0 == 0x%x * X**2 + 0x%x * X + 0x%x' % (x2,x1,x0))
		if x2 != 1:
			return
		assert x2 == 1
		if x1%2 != 0:
			return
		assert x1%2 == 0
		#print('0 == (X + 0x%x) ** 2 + 0x%x'%(x1//2,(x0-(x1//2)**2)%2**32))
		x3 = ((x1//2)**2-x0)%2**32
		#print('(X + 0x%x) ** 2 == 0x%x'%(x1//2,x3))
		sqrarr = sqrt_pow32(x3)
		#print(sqrarr)
		for x4 in sqrarr:
			X = (x4 - x1//2) % 2**32
			Y = (s1 - X) % 2**32

			#print(arr+[X,Y],(s+X+Y)%2**32, (p*X*Y)%2**32)
			#print(arr+[hex(X),hex(Y)],(s+X+Y)%2**32, (p*X*Y)%2**32)
			return arr+[X,Y]
			if (4*X+0x1c0) % 2**32 < 0x1000 and (4*Y+0x1c0) % 2**32 < 0x1000:
				#print('JACKPOT!', arr, X, Y)
				return arr+[X,Y]
				sys.exit(0)

	# X + Y + Z == 45; X * Y * Z == 362880
	# Y = 45 - X - Z
	# X * (45-X-Z) * Z == 362880
	# Z**2 - 45*X*Z + 362880/X == 0
	# (Z-45*X/2)**2 - (45*X/2)**2 + 362880/X == 0
	# (Z-45*X/2)**2 == (45*X/2)**2 - 362880/X
	# X=2 -> (Z-45)**2 = 

	# 45*X += sqrt ((45*X)**2 - 4*362880/X) // 2

if __name__ == '__main__':

	r9mod = solve_row([0xffffff97,0x08048799,1,1,1,1,1])
	assert r9mod is not None

	r9 = [r9mod[2],r9mod[7],r9mod[3],r9mod[4],r9mod[0],r9mod[8],r9mod[5],r9mod[6],r9mod[1]]

	for i in [7,1,4,8,5,2,3,6,9]:
		print(('%d '*9 % tuple(r9[i:9]+r9[0:i])).strip())

