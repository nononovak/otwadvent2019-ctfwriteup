#!/usr/bin/env python3

import csv

N7110_KEYPAD_ZERO = 0
N7110_KEYPAD_ONE = 1
N7110_KEYPAD_TWO = 2
N7110_KEYPAD_THREE = 3
N7110_KEYPAD_FOUR = 4
N7110_KEYPAD_FIVE = 5
N7110_KEYPAD_SIX = 6
N7110_KEYPAD_SEVEN = 7
N7110_KEYPAD_EIGHT = 8
N7110_KEYPAD_NINE = 9
N7110_KEYPAD_STAR = 10
N7110_KEYPAD_HASH = 11
N7110_KEYPAD_MENU_LEFT = 100
N7110_KEYPAD_MENU_RIGHT = 101
N7110_KEYPAD_MENU_UP = 102
N7110_KEYPAD_MENU_DOWN = 103
N7110_KEYPAD_CALL_ACCEPT = 104
N7110_KEYPAD_CALL_REJECT = 105

'''
enum {
    N7110_IME_T9 = 0,
    N7110_IME_T9_CAPS = 1,
    N7110_IME_ABC = 2,
    N7110_IME_ABC_CAPS = 3
} N7110_IME_METHODS;

#define N7110_KEYPAD_ZERO_ABC_CHARS  " 0"
#define N7110_KEYPAD_ONE_ABC_CHARS   ".,'?!\"1-()@/:"
#define N7110_KEYPAD_TWO_ABC_CHARS   "abc2"
#define N7110_KEYPAD_THREE_ABC_CHARS "def3"
#define N7110_KEYPAD_FOUR_ABC_CHARS  "ghi4"
#define N7110_KEYPAD_FIVE_ABC_CHARS  "jkl5"
#define N7110_KEYPAD_SIX_ABC_CHARS   "mno6"
#define N7110_KEYPAD_SEVEN_ABC_CHARS "pqrs7"
#define N7110_KEYPAD_EIGHT_ABC_CHARS "tuv8"
#define N7110_KEYPAD_NINE_ABC_CHARS  "wxyz9"
#define N7110_KEYPAD_STAR_ABC_CHARS  "@/:_;+&%*[]{}"
#define N7110_KEYPAD_HASH_CHARS N7110_IME_METHODS
'''

def output_char(t,ch,n):
	#print(t,ch,n)

	KEYPAD_LOOKUP = {
		0:" 0",
		1:".,'?!\"1-()@/:",
		2:"abc2",
		3:"def3",
		4:"ghi4",
		5:"jkl5",
		6:"mno6",
		7:"pqrs7",
		8:"tuv8",
		9:"wxyz9",
		10:"@/:_;+&%*[]{}",
	}

	ret = '[%d,%d]'%(ch,n)

	if ch in KEYPAD_LOOKUP:
		st = KEYPAD_LOOKUP[ch]
		ret = st[n%len(st)]

	#print('OUTPUT:', ret)
	return ret

if __name__ == '__main__':
	csv_file = open('sms4.csv','r')

	last_time = 0
	last_char = -1
	count = 0
	ans = ''
	for row in csv.reader(csv_file):
		next_time = int(row[0])
		diff_time = next_time-last_time

		ch = int(row[1])

		if last_char == ch and diff_time < 1000:
			count += 1
		else:
			ans = ans + output_char(last_time, last_char, count)
			count = 0

		#print(row)
		last_time = next_time
		last_char = ch

	ans = ans + output_char(last_time, last_char, count)

	print('ANSWER:', ans)
