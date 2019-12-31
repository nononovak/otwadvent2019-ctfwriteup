# Day 15 - Self-Replicating Toy - rev

> Can you design your own self-replicating toy?

Service: nc 3.93.128.89 1214

Download: [dc3f15513e6d0ca076135b4a05fa954d62938670ddd7db88168d68c00e488b87-chal.c](https://advent2019.s3.amazonaws.com/dc3f15513e6d0ca076135b4a05fa954d62938670ddd7db88168d68c00e488b87-chal.c)

## Initial Analysis

For this problem, we're presented with a [c source file](./static/dc3f15513e6d0ca076135b4a05fa954d62938670ddd7db88168d68c00e488b87-chal.c). After staring at this file a while, I came up with the basic rules for the challenge:

* A set of instructions are defined for different byte values
* We provide "assemblium" instructions to be executed
* Some of these instructions write data to the "stack"
* Some of these instructions perform arithmetic operations on "stack" data
* Some of these instructions write "stack" data to the "output"
* Some of these instructions define new "functions"
* If the "output" of our complete "assemblium" instructions matches the instructions, then we get a flag

## Solving

I tried a bunch of methods to solve this problem, but eventually came up with the following strategy.

1. Create a bunch of functions, each of which: (1) "outputs" a byte X, (2) pushes instructions to write the function instruction value to the "stack"
2. Once all of these functions are created, call each of the functions in the right order to "output" the function-creation instructions
3. Create a "function" to "output" each of the instructions on the "stack" (which should be the "function" instructions themselves)
4. Execute that new last "function".

There is a little bookkeeping with this technique that I'm glossing over. Mostly that some of these steps require us to reverse the operations on the "stack" before putting them in the "output", so we have to play games with "function" creation and execution, but it does work in the end.

Honestly, there isn't really a simple way to explain how this works aside from looking at my [solution python script](./solutions/day15_solver.py). Running it against the server gives the flag:

```
$ ./solutions/day15_solver.py 
21 80 03 80 20 10 00 80 00 00 00 80 00 40 30 80 00 00 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 40 01 30 80 01 01 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 40 02 30 80 02 02 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 02 01 30 80 04 01 02 83 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 40 04 30 80 08 04 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 04 01 30 80 10 01 04 83 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 04 02 30 80 20 02 04 83 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 40 04 02 01 30 80 40 01 02 04 83 83 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 40 08 30 80 00 80 00 08 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 08 01 30 80 00 80 01 02 83 01 08 83 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 08 02 30 80 00 80 20 02 08 83 a0
21 80 41 80 20 80 01 40 80 20 80 00 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 40 08 02 01 01 02 08 83 83 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 08 04 30 80 03 80 20 01 04 08 83 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 40 08 04 01 30 80 03 80 02 01 01 04 08 83 83 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 40 08 04 02 30 80 03 80 20 10 02 04 08 83 83 a0
21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 03 80 40 08 04 02 01 30 80 03 80 40 01 01 02 04 08 83 83 83 a0
40 80 00 80 30
40 80 b0
40 80 00 80 30
40 80 00 80 30
missing: []
================================================================================
21 80 03 80 20 10 00 80 00 00 00 80 00 40 30 80 00 00 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 40 01 30 80 01 01 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 40 02 30 80 02 02 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 02 01 30 80 04 01 02 83 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 40 04 30 80 08 04 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 04 01 30 80 10 01 04 83 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 04 02 30 80 20 02 04 83 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 40 04 02 01 30 80 40 01 02 04 83 83 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 40 08 30 80 00 80 00 08 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 08 01 30 80 00 80 01 02 83 01 08 83 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 08 02 30 80 00 80 20 02 08 83 a0 21 80 41 80 20 80 01 40 80 20 80 00 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 40 08 02 01 01 02 08 83 83 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 40 08 04 30 80 03 80 20 01 04 08 83 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 40 08 04 01 30 80 03 80 02 01 01 04 08 83 83 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 40 08 04 02 30 80 03 80 20 10 02 04 08 83 83 a0 21 80 03 80 20 10 00 80 00 00 00 80 00 03 80 03 80 03 80 03 80 40 08 04 02 01 30 80 03 80 40 01 01 02 04 08 83 83 83 a0 21 80 21 80 cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 c7 ce c8 c0 c0 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 c7 c1 ce c8 c1 c1 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 c7 c2 ce c8 c2 c2 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 c7 c2 c1 ce c8 c3 c1 c2 c9 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 c7 c3 ce c8 c4 c3 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 c7 c3 c1 ce c8 c5 c1 c3 c9 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 c7 c3 c2 ce c8 c6 c2 c3 c9 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 cd c8 c7 c3 c2 c1 ce c8 c7 c1 c2 c3 c9 c9 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 c7 c4 ce c8 c0 c8 c0 c4 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 c7 c4 c1 ce c8 c0 c8 c1 c2 c9 c1 c4 c9 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 c7 c4 c2 ce c8 c0 c8 c6 c2 c4 c9 ca cc c8 cf c8 c6 c8 c1 c7 c8 c6 c8 c0 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 cd c8 c7 c4 c2 c1 c1 c2 c4 c9 c9 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 c7 c4 c3 ce c8 cd c8 c6 c1 c3 c4 c9 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 cd c8 c7 c4 c3 c1 ce c8 cd c8 c2 c1 c1 c3 c4 c9 c9 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 cd c8 c7 c4 c3 c2 ce c8 cd c8 c6 c5 c2 c3 c4 c9 c9 ca cc c8 cd c8 c6 c5 c0 c8 c0 c0 c0 c8 c0 cd c8 cd c8 cd c8 cd c8 c7 c4 c3 c2 c1 ce c8 cd c8 c7 c1 c1 c2 c3 c4 c9 c9 c9 ca cc c8 cc c8 cb
b"We just discovered a strange element called Assemblium.\nThey are like mini robots. There are different isotopes, each having\ndifferent behavior... though we haven't figured that out exactly yet.\n\nBut I've got a great idea - why don't we build a toy that replicates\nitself? That would eliminate all our human, ahem, elvian costs.\n\nLet's do this!\n\nLength of your Assemblium sequence: "
>> b'931\n'
b'Enter your Assemblium sequence:\n'
b'Enter your Assemblium sequence:\n'
>> b'!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00@0\x80\x00\x00\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80@\x010\x80\x01\x01\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80@\x020\x80\x02\x02\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80@\x02\x010\x80\x04\x01\x02\x83\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80@\x040\x80\x08\x04\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80@\x04\x010\x80\x10\x01\x04\x83\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80@\x04\x020\x80 \x02\x04\x83\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80\x03\x80@\x04\x02\x010\x80@\x01\x02\x04\x83\x83\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80@\x080\x80\x00\x80\x00\x08\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80@\x08\x010\x80\x00\x80\x01\x02\x83\x01\x08\x83\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80@\x08\x020\x80\x00\x80 \x02\x08\x83\xa0!\x80A\x80 \x80\x01@\x80 \x80\x00\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80\x03\x80@\x08\x02\x01\x01\x02\x08\x83\x83\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80@\x08\x040\x80\x03\x80 \x01\x04\x08\x83\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80\x03\x80@\x08\x04\x010\x80\x03\x80\x02\x01\x01\x04\x08\x83\x83\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80\x03\x80@\x08\x04\x020\x80\x03\x80 \x10\x02\x04\x08\x83\x83\xa0!\x80\x03\x80 \x10\x00\x80\x00\x00\x00\x80\x00\x03\x80\x03\x80\x03\x80\x03\x80@\x08\x04\x02\x010\x80\x03\x80@\x01\x01\x02\x04\x08\x83\x83\x83\xa0!\x80!\x80\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xc7\xce\xc8\xc0\xc0\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xc7\xc1\xce\xc8\xc1\xc1\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xc7\xc2\xce\xc8\xc2\xc2\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xc7\xc2\xc1\xce\xc8\xc3\xc1\xc2\xc9\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xc7\xc3\xce\xc8\xc4\xc3\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xc7\xc3\xc1\xce\xc8\xc5\xc1\xc3\xc9\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xc7\xc3\xc2\xce\xc8\xc6\xc2\xc3\xc9\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xcd\xc8\xc7\xc3\xc2\xc1\xce\xc8\xc7\xc1\xc2\xc3\xc9\xc9\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xc7\xc4\xce\xc8\xc0\xc8\xc0\xc4\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xc7\xc4\xc1\xce\xc8\xc0\xc8\xc1\xc2\xc9\xc1\xc4\xc9\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xc7\xc4\xc2\xce\xc8\xc0\xc8\xc6\xc2\xc4\xc9\xca\xcc\xc8\xcf\xc8\xc6\xc8\xc1\xc7\xc8\xc6\xc8\xc0\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xcd\xc8\xc7\xc4\xc2\xc1\xc1\xc2\xc4\xc9\xc9\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xc7\xc4\xc3\xce\xc8\xcd\xc8\xc6\xc1\xc3\xc4\xc9\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xcd\xc8\xc7\xc4\xc3\xc1\xce\xc8\xcd\xc8\xc2\xc1\xc1\xc3\xc4\xc9\xc9\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xcd\xc8\xc7\xc4\xc3\xc2\xce\xc8\xcd\xc8\xc6\xc5\xc2\xc3\xc4\xc9\xc9\xca\xcc\xc8\xcd\xc8\xc6\xc5\xc0\xc8\xc0\xc0\xc0\xc8\xc0\xcd\xc8\xcd\xc8\xcd\xc8\xcd\xc8\xc7\xc4\xc3\xc2\xc1\xce\xc8\xcd\xc8\xc7\xc1\xc1\xc2\xc3\xc4\xc9\xc9\xc9\xca\xcc\xc8\xcc\xc8\xcb'
b'Congratulations!'
b'Congratulations!\n\nAOTW{G0od_job_'
b'Congratulations!\n\nAOTW{G0od_job_writing_y0ur_v3r'
b'Congratulations!\n\nAOTW{G0od_job_writing_y0ur_v3ry_0wN_quin3!}\n'
b'Congratulations!\n\nAOTW{G0od_job_writing_y0ur_v3ry_0wN_quin3!}\n'
```
