#!/usr/bin/env python3

from pprint import pprint
import sys
import pycosat
import time

########

def solve_problem(problemset):
	print('Problem:') 
	problemset = [arr*1 for arr in problemset]
	pprint(problemset)  
	solve(problemset) 
	print('Answer:')
	pprint(problemset)
	if problemset[0][0] != None:
		sys.exit(0)
	
def v(i, j, d): 
	#return 81 * (i - 1) + 9 * (j - 1) + d
	return 100 * (i - 1) + 10 * (j - 1) + d

#Reduces Sudoku problem to a SAT clauses 
def sudoku_clauses(): 
	res = []
	#print('# for all cells, ensure that the each cell:')
	for i in range(1, 10):
		for j in range(1, 10):
			#print('# denotes (at least) one of the 9 digits (1 clause)')
			res.append([v(i, j, d) for d in range(1, 10)])
			#print(res[-1])
			#print('# does not denote two different digits at once (36 clauses)')
			for d in range(1, 10):
				for dp in range(d + 1, 10):
					res.append([-v(i, j, d), -v(i, j, dp)])
					#print(res[-1])

	def valid(cells): 
		for i, xi in enumerate(cells):
			for j, xj in enumerate(cells):
				if i < j:
					for d in range(1, 10):
						res.append([-v(xi[0], xi[1], d), -v(xj[0], xj[1], d)])
						#print(res[-1])

	#print('# ensure rows and columns have distinct values')
	for i in range(1, 10):
		valid([(i, j) for j in range(1, 10)])
		valid([(j, i) for j in range(1, 10)])
		
	#print('# ensure 3x3 sub-grids "regions" have distinct values')
	for i in 1, 4, 7:
		for j in 1, 4 ,7:
			valid([(i + k % 3, j + k // 3) for k in range(9)])
	  
	assert len(res) == 81 * (1 + 36) + 27 * 324
	return res

def solve(grid):
	#solve a Sudoku problem
	clauses = sudoku_clauses()
	for i in range(1, 10):
		for j in range(1, 10):
			d = grid[i - 1][j - 1]
			#print('# For each digit already known, a clause (with one literal). ')
			if d:
				clauses.append([v(i, j, d)])
				#print(clauses[-1])
	
	# Print number SAT clause  
	numclause = len(clauses)
	print("P CNF " + str(numclause) +"(number of clauses)")
	
	# solve the SAT problem
	start = time.time()
	sol = set(pycosat.solve(clauses))
	#print(sol)
	end = time.time()
	print("Time: "+str(end - start))
	
	def read_cell(i, j):
		# return the digit of cell i, j according to the solution
		for d in range(1, 10):
			if v(i, j, d) in sol:
				return d

	for i in range(1, 10):
		for j in range(1, 10):
			grid[i - 1][j - 1] = read_cell(i, j)

#########

def parse_constraint(st):
	st0 = 'ABCDEFGHI'
	st1 = '123456789'
	params,val = tuple(st.split('='))
	params = [x.strip() for x in params.split('+')]
	params = [(st0.index(x[0]),st1.index(x[1])) for x in params]
	val = int(val)
	return params,val

CONSTRAINTS = []
CONSTRAINTS.append(parse_constraint('B9 + B8 + C1 + H4 + H4 = 23'))
CONSTRAINTS.append(parse_constraint('A5 + D7 + I5 + G8 + B3 + A5 = 19'))
CONSTRAINTS.append(parse_constraint('I2 + I3 + F2 + E9 = 15'))
CONSTRAINTS.append(parse_constraint('I7 + H8 + C2 + D9 = 26'))
CONSTRAINTS.append(parse_constraint('I6 + A5 + I3 + B8 + C3 = 20'))
CONSTRAINTS.append(parse_constraint('I7 + D9 + B6 + A8 + A3 + C4 = 27'))
CONSTRAINTS.append(parse_constraint('C7 + H9 + I7 + B2 + H8 + G3 = 31'))
CONSTRAINTS.append(parse_constraint('D3 + I8 + A4 + I6 = 27'))
CONSTRAINTS.append(parse_constraint('F5 + B8 + F8 + I7 + F1 = 33'))
CONSTRAINTS.append(parse_constraint('A2 + A8 + D7 + E4 = 21'))
CONSTRAINTS.append(parse_constraint('C1 + I4 + C2 + I1 + A4 = 20'))
CONSTRAINTS.append(parse_constraint('F8 + C1 + F6 + D3 + B6 = 25'))

def check_extra_constraint(grid,arr,val,verbose=False):
	s = 0
	is_null = False
	for (y,x) in arr:
		if grid[y][x] == 0:
			is_null = True
			break
		s += grid[y][x]
	if verbose:
		print('extra:', is_null, arr, [grid[y][x] for (y,x) in arr], s, val)
	if not is_null and s != val:
		return False
	return True

def check_constraints(grid,this_idx):

	(this_y,this_x) = this_idx
	this_val = grid[this_y][this_x]
	# check rows and columns
	for x in range(9):
		if x != this_x and this_val == grid[this_y][x]:
			#print('invalidx',x,this_idx)
			return False
	for y in range(9):
		if y != this_y and this_val == grid[y][this_x]:
			#print('invalidy',y,this_idx)
			return False

	# check 3x3
	start_x = this_x-(this_x%3)
	start_y = this_y-(this_y%3)
	for x in range(3):
		for y in range(3):
			if this_x != x+start_x and this_y != y+start_y and this_val == grid[y+start_y][x+start_x]:
				#print('invalid3x3',grid[this_y][this_x],x,y,this_idx)
				return False

	# check extra constraints
	for cons_arr, cons_val in CONSTRAINTS:
		if not check_extra_constraint(grid, cons_arr, cons_val):
			return False

	return True

def exhaust(grid,constraint_idx):
	if constraint_idx >= len(CONSTRAINT_ARR):
		print('complete')
		pprint([arr*1 for arr in grid])
		solve_problem(grid)
		return
	#if constraint_idx >= 28:
	#	print('working on', constraint_idx, '...')
	#	pprint(grid)
	(this_y,this_x) = CONSTRAINT_ARR[constraint_idx]

	new_grid = [grid[y]*1 for y in range(9)]
	for val in range(1,10):
		new_grid[this_y][this_x] = val
		if check_constraints(new_grid,CONSTRAINT_ARR[constraint_idx]):
			exhaust(new_grid,constraint_idx+1)

	return True

GRID = [[0, 0, 0, 0, 0, 0, 0, 0, 1],
		[0, 1, 2, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 2, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0, 2],
		[0, 2, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 1, 2, 0],
		[1, 0, 0, 0, 0, 2, 0, 0, 0],
		[0, 0, 0, 1, 0, 0, 0, 0, 0]]

CONSTRAINT_ARR = []
for arr,val in CONSTRAINTS:
	for x in arr:
		if x in CONSTRAINT_ARR:
			continue
		if GRID[x[0]][x[1]] == 0:
			CONSTRAINT_ARR.append(x)

if __name__ == '__main__':

	print(len(CONSTRAINT_ARR), CONSTRAINT_ARR)

	#exhaust(grid,(0,0))
	exhaust(GRID,0)

'''
Answer:
[[8, 6, 4, 7, 2, 9, 5, 3, 1],
 [9, 1, 2, 4, 5, 3, 7, 6, 8],
 [3, 7, 5, 6, 1, 8, 2, 4, 9],
 [6, 4, 9, 8, 7, 5, 3, 1, 2],
 [7, 2, 1, 9, 3, 6, 8, 5, 4],
 [5, 3, 8, 2, 4, 1, 6, 9, 7],
 [4, 8, 6, 5, 9, 7, 1, 2, 3],
 [1, 9, 7, 3, 6, 2, 4, 8, 5],
 [2, 5, 3, 1, 8, 4, 9, 7, 6]]

AOTW{86472953189247356794813521457639}

'''
