#!/usr/bin/env python3

import requests
import time
import base64
import sys
import binascii
import json
import os

AMOUNT = 1e64

def get_new(name='joe'):
	#return 'IEMfoZo01BJQIrsx4gImboCFHs94XpqR/BQ6+nmrkCU='
	r = requests.post('http://3.93.128.89:1217/control',json={'action':'new','name':name})
	print(r.reason, r.text)
	print(r.json())
	_id = r.json()['id']
	return _id

def get_state(_id):
	j = {'action':'state','snowflakes': 99999, 'speed_upgrade_cost': 3333.333,'amount':234567,'collect_speed':-1}
	print(j)
	r = requests.post('http://3.93.128.89:1217/client',json=j,headers={'Cookie':'id='+_id})
	print(r.json())
	j = r.json()
	speed = j['collect_speed']
	count = j['snowflakes']
	upgrd = j['speed_upgrade_cost']
	time.sleep(1)
	return (speed,count,upgrd)

def collect(_id,n=AMOUNT):
	j = {'action':'collect','snowflakes': 99999, 'speed_upgrade_cost': 3333.333,'amount':n,'collect_speed':-1}
	print(j)
	r = requests.post('http://3.93.128.89:1217/client',json=j,headers={'Cookie':'id='+_id})
	return

def melt(_id):
	j = {'action':'melt','amount':AMOUNT,'snowflakes': 99999, 'speed_upgrade_cost': 3333.333,'collect_speed':-1}
	print(j)
	r = requests.post('http://3.93.128.89:1217/client',json=j,headers={'Cookie':'id='+_id})
	return

def upgrade(_id):
	j = {'action':'upgrade','amount':AMOUNT,'snowflakes': 99999, 'speed_upgrade_cost': 3333.333,'collect_speed':-1}
	print(j)
	r = requests.post('http://3.93.128.89:1217/client',json=j,headers={'Cookie':'id='+_id})
	return

def custom(_id,action):
	j = {'action':action,'amount':AMOUNT,'snowflakes': 99999, 'speed_upgrade_cost': 3333.333,'collect_speed':-1}
	print(j)
	r = requests.post('http://3.93.128.89:1217/client',json=j,headers={'Cookie':'id='+_id})
	print(r.text)
	print(r.headers)
	return

def save(_id,data):
	j = {'action':'save','data':data}
	print(j)
	r = requests.post('http://3.93.128.89:1217/control',json=j,headers={'Cookie':'id='+_id})
	return r.json()

def buy_flag(_id):
	j = {'action':'buy_flag','amount':AMOUNT,'snowflakes': 99999, 'speed_upgrade_cost': 3333.333,'collect_speed':-1}
	print(j)
	r = requests.post('http://3.93.128.89:1217/client',json=j,headers={'Cookie':'id='+_id})
	return

def history(_id):
	r = requests.get('http://3.93.128.89:1217/history/client',headers={'Cookie':'id='+_id})
	j = r.json()
	print(j)
	return j

def history_control(_id):
	r = requests.get('http://3.93.128.89:1217/history/control',headers={'Cookie':'id='+_id})
	print(r.text)
	j = r.json()
	print(j)
	return j

def xor(bin_1,bin_2):
	arr = []
	for i in range(min(len(bin_1),len(bin_2))):
		arr.append(bin_1[i]^bin_2[i])
	return bytes(arr)

def xor64(b64_1,b64_2):
	bin_1 = base64.b64decode(b64_1)
	bin_2 = base64.b64decode(b64_2)
	return xor(bin_1,bin_2)

if __name__ == '__main__':

	os.environ.setdefault('HTTP_PROXY','http://localhost:8080')

	print(binascii.hexlify(xor64('ZPndFWsM0ioUz8an0yfUmssOGAp7+YpaNEWLKkCOm+zBMdSa2Q0ZCT2m','ZPndFWsM0ioUz8en0yfUmssOGAp7+YpaNEWLKkCOm+zBMdSa2Q0ZCT2m'))) # 1
	print(binascii.hexlify(xor64('ZPndFWsM0ioUz8an0yfUmssOGAp7+YpaNEWLKkCOm+zBMdSa2Q0ZCT2m','ZPndFWsM0ioUz8e5zTvYmJoNDQp6v5JAJViHKAyBl+SGKc6Ymh8OC3n5zQ=='))) # 10
	print(binascii.hexlify(xor64('ZPndFWsM0ioUz8an0yfUmssOGAp7+YpaNEWLKkCOm+zBMdSa2Q0ZCT2m','ZPndFWsM0ioUz8e4zTvYmJoNDQp6v5JAJViHKAyBl+SGKc6Ymh8OC3n5zQ=='))) # 11
	print(binascii.hexlify(xor64('ZPndFWsM0ioUz8an0yfUmssOGAp7+YpaNEWLKkCOm+zBMdSa2Q0ZCT2m','ZPndFWsM0ioUz8an0yfUmssOGAp7+YpaN0WLKkCOm+zBMdSa2Q0ZCT2m')))
	print(binascii.hexlify(xor64('ZPndFWsM0ioUz8an0yfUmssOGAp7+YpaNEWLKkCOm+zBMdSa2Q0ZCT2m','ZPndFWsM0ioUz8e5zTvYmJoNDQp6v5JAJVuHKAyBl+SGKc6Ymh8OC3n5zQ==')))
	print(binascii.hexlify(xor64('ZPndFWsM0ioUz8an0yfUmssOGAp7+YpaNEWLKkCOm+zBMdSa2Q0ZCT2m','ZPndFWsM0ioUz8en2zLNgYFHRFYm4olDPFCTPgLP1PqTbpHcmkRdXDP7khRkBM4qFM/U6JBvkprF')))

	print(binascii.hexlify(xor64('6/T/0XUxkRK6FgpDJOOLoBuOw+P09KieKnjIEu5XVwg29YugCY3C4LKr','6/T/0XUxkRK6FhdcOv+HokqN1uP1srCEO2XEEKJYWwBx7ZGiSp/V4vb07w=='))) # -1
	print(binascii.hexlify(xor64('6/T/0XUxkRK6FgpDJOOLoBuOw+P09KieKnjIEu5XVwg29YugCY3C4LKr','6/T/0XUxkRK6FgtdOv+HokqN1uP1srCEO2XEEKJYWwBx7ZGiSp/V4vb07w=='))) # 10
	print(binascii.hexlify(xor64('6/T/0XUxkRK6FhdcOv+HokqN1uP1srCEO2XEEKJYWwBx7ZGiSp/V4vb07w==','6/T/0XUxkRK6FgtdOv+HokqN1uP1srCEO2XEEKJYWwBx7ZGiSp/V4vb07w=='))) # 10

	val1 = base64.b64decode('ZPndFWsM0ioUz8an0yfUmssOGAp7+YpaNEWLKkCOm+zBMdSa2Q0ZCT2m') # 0
	val2 = base64.b64decode('ZPndFWsM0ioUz8e5zTvYmJoNDQp6v5JAJViHKAyBl+SGKc6Ymh8OC3n5zQ==') # 10
	val3 = base64.b64decode('ZPndFWsM0ioUz8en2zLNgYFHRFYm4olDPFCTPgLP1PqTbpHcmkRdXDP7khRkBM4qFM/U6JBvkprF')
	diff = xor(val1, val2)
	key = {}
	key[10] = ord('0')^val1[10]
	assert key[10] == ord('1')^val2[10]
	key[11] = ord('0')^val2[11]
	pln1 = {}
	pln2 = {}
	# create the key by walking the string with our assumption
	for i in range(11,len(diff)):
		key[i+1] = key[i]^val1[i] ^ val2[i+1]

	k = bytes([key.get(i,0) for i in range(len(diff))])
	print(xor(val1,k))
	print(xor(val2,k))
	print(xor(val3,k))

	# perform the attack live
	_id = get_new('john')
	get_state(_id)
	history(_id)
	arr = history_control(_id)
	first_val_pln = bytes(10) + b'0.0, "speed": 1, "name": "john"}'
	first_val_cip = base64.b64decode(arr[1][1]['data'])
	explt_val_pln = bytes(10) + b'1e+64,"speed":1,"name":"john"}'
	key = xor(first_val_pln,first_val_cip)
	print(key)
	next_val_pln = xor(explt_val_pln,key)

	print(arr)

	get_state(_id)
	save(_id,base64.b64encode(next_val_pln).decode('ascii'))
	get_state(_id)

	history(_id)
	arr2 = history_control(_id)

	buy_flag(_id)
	get_state(_id)
