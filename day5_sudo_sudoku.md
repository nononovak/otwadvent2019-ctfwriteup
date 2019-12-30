# Day 5 - Sudo Sudoku - misc, sudoku

> Santa's little helpers are notoriously good at solving Sudoku puzzles, so they made a special variant...

Download: [2a3fad4ea8987eb63b5abdea1c8bdc75d4f2e6b087388c5e33cec99136b4257a-sudosudoku.tar.xz](https://advent2019.s3.amazonaws.com/2a3fad4ea8987eb63b5abdea1c8bdc75d4f2e6b087388c5e33cec99136b4257a-sudosudoku.tar.xz)

## Initial Analysis

The problem's `challenge.txt` files reads as follows:

```
Santa's little helpers are notoriously good at solving Sudoku puzzles.
Because regular Sudoku puzzles are too trivial, they have invented a variant.

    1 2 3   4 5 6   7 8 9
  +-------+-------+-------+
A | . . . | . . . | . . 1 |
B | . 1 2 | . . . | . . . |
C | . . . | . . . | 2 . . |
  +-------+-------+-------+
D | . . . | . . . | . . 2 |
E | . 2 . | . . . | . . . |
F | . . . | . . . | . . . |
  +-------+-------+-------+
G | . . . | . . . | 1 2 . |
H | 1 . . | . . 2 | . . . |
I | . . . | 1 . . | . . . |
  +-------+-------+-------+

In addition to the standard Sudoku puzzle above,
the following equations must also hold:

B9 + B8 + C1 + H4 + H4 = 23
A5 + D7 + I5 + G8 + B3 + A5 = 19
I2 + I3 + F2 + E9 = 15
I7 + H8 + C2 + D9 = 26
I6 + A5 + I3 + B8 + C3 = 20
I7 + D9 + B6 + A8 + A3 + C4 = 27
C7 + H9 + I7 + B2 + H8 + G3 = 31
D3 + I8 + A4 + I6 = 27
F5 + B8 + F8 + I7 + F1 = 33
A2 + A8 + D7 + E4 = 21
C1 + I4 + C2 + I1 + A4 = 20
F8 + C1 + F6 + D3 + B6 = 25

If you then read the numbers clockwise starting from A1 to A9, to I9, to I1 and
back to A1, you end up with a number with 32 digits.  Enclose that in AOTW{...}
to get the flag.

```

As the challenge describes, the objective is to solve the Sudoku puzzle with the additional constraints. Rather than do the math for this puzzle manually, I wrote a [short script](./solutions/day5_solver.py) to brute force the problem for me. Roughly speaking, this script reads all of the constraints, sets up a loop to brute force them all, and once all of the constraints are met it calls a [SAT solver](https://github.com/taufanardi/sudoku-sat-solver/blob/38d601547b04bf22591c14e1746cbe70cb777be7/Sudoku.py) to solve the remainder of the Sudoku puzzle. If a solution is found, then it outputs it and breaks, otherwise it continues on. Each sudoku solve takes less than a second, so the main computational bottleneck is the brute force of the constraints up front. The final output of the script gives the answer and the flag:

```
$ time ./solutions/day5_solver.py 
32 [(1, 8), (1, 7), (2, 0), (7, 3), (0, 4), (3, 6), (8, 4), (8, 1), (8, 2), (5, 1), (4, 8), (8, 6), (7, 7), (2, 1), (8, 5), (2, 2), (1, 5), (0, 7), (0, 2), (2, 3), (7, 8), (6, 2), (3, 2), (8, 7), (0, 3), (5, 4), (5, 7), (5, 0), (0, 1), (4, 3), (8, 0), (5, 5)]

<snip>

complete
[[0, 6, 4, 7, 2, 0, 0, 3, 1],
 [0, 1, 2, 0, 0, 3, 0, 6, 8],
 [3, 7, 5, 6, 0, 0, 2, 0, 0],
 [0, 0, 9, 0, 0, 0, 3, 0, 2],
 [0, 2, 0, 9, 0, 0, 0, 0, 4],
 [5, 3, 0, 0, 4, 1, 0, 9, 0],
 [0, 0, 6, 0, 0, 0, 1, 2, 0],
 [1, 0, 0, 3, 0, 2, 0, 8, 5],
 [2, 5, 3, 1, 8, 4, 9, 7, 0]]
Problem:
[[0, 6, 4, 7, 2, 0, 0, 3, 1],
 [0, 1, 2, 0, 0, 3, 0, 6, 8],
 [3, 7, 5, 6, 0, 0, 2, 0, 0],
 [0, 0, 9, 0, 0, 0, 3, 0, 2],
 [0, 2, 0, 9, 0, 0, 0, 0, 4],
 [5, 3, 0, 0, 4, 1, 0, 9, 0],
 [0, 0, 6, 0, 0, 0, 1, 2, 0],
 [1, 0, 0, 3, 0, 2, 0, 8, 5],
 [2, 5, 3, 1, 8, 4, 9, 7, 0]]
P CNF 11788(number of clauses)
Time: 0.003549814224243164
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

real	1m4.114s
user	1m3.817s
sys	0m0.181s
```

With this output, the flag is: `AOTW{86472953189247356794813521457639}`
