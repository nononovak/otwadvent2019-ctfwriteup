# Day 10 - ChristmaSSE KeyGen - rev, math

> I ran this program but it never finished... maybe my computer is too slow. Maybe yours is faster?

Download: [326c15f8884fcc13d18a60e2fb933b0e35060efa8a44214e06d589e4e235fe34](https://advent2019.s3.amazonaws.com/326c15f8884fcc13d18a60e2fb933b0e35060efa8a44214e06d589e4e235fe34)

Mirror: [326c15f8884fcc13d18a60e2fb933b0e35060efa8a44214e06d589e4e235fe34](./images/326c15f8884fcc13d18a60e2fb933b0e35060efa8a44214e06d589e4e235fe34)

# Initial Analysis

This problem is an x86 reversing challenge. Opening up the binary in your favorite decompiler you'll see that the main function uses a lot of packed dword instructions. The main function is short enough, so I've included it below (output from `objdump`)

```
0000000000400570 <main>:
  400570:	66 0f 6f 05 08 0b 20 	movdqa 0x200b08(%rip),%xmm0        # 601080 <data+0x40>
  400577:	00 
  400578:	66 0f 70 d8 54       	pshufd $0x54,%xmm0,%xmm3
  40057d:	66 0f 70 d0 51       	pshufd $0x51,%xmm0,%xmm2
  400582:	66 0f 70 c8 45       	pshufd $0x45,%xmm0,%xmm1
  400587:	66 0f 70 c0 15       	pshufd $0x15,%xmm0,%xmm0
  40058c:	31 c0                	xor    %eax,%eax
  40058e:	48 b9 15 81 e9 7d f4 	movabs $0x112210f47de98115,%rcx
  400595:	10 22 11 
  400598:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  40059f:	00 
  4005a0:	0f ae f8             	sfence 
  4005a3:	66 44 0f 6f 0d 94 0a 	movdqa 0x200a94(%rip),%xmm9        # 601040 <data>
  4005aa:	20 00 
  4005ac:	66 41 0f 70 f1 00    	pshufd $0x0,%xmm9,%xmm6
  4005b2:	66 0f 38 40 f3       	pmulld %xmm3,%xmm6
  4005b7:	66 45 0f 70 e1 55    	pshufd $0x55,%xmm9,%xmm12
  4005bd:	66 44 0f 38 40 e2    	pmulld %xmm2,%xmm12
  4005c3:	66 44 0f fe e6       	paddd  %xmm6,%xmm12
  4005c8:	66 44 0f 6f 15 7f 0a 	movdqa 0x200a7f(%rip),%xmm10        # 601050 <data+0x10>
  4005cf:	20 00 
  4005d1:	66 45 0f 70 c2 00    	pshufd $0x0,%xmm10,%xmm8
  4005d7:	66 44 0f 38 40 c3    	pmulld %xmm3,%xmm8
  4005dd:	66 44 0f 6f 2d 7a 0a 	movdqa 0x200a7a(%rip),%xmm13        # 601060 <data+0x20>
  4005e4:	20 00 
  4005e6:	66 45 0f 70 dd 00    	pshufd $0x0,%xmm13,%xmm11
  4005ec:	66 44 0f 38 40 db    	pmulld %xmm3,%xmm11
  4005f2:	66 44 0f 6f 3d 75 0a 	movdqa 0x200a75(%rip),%xmm15        # 601070 <data+0x30>
  4005f9:	20 00 
  4005fb:	66 45 0f 70 f7 00    	pshufd $0x0,%xmm15,%xmm14
  400601:	66 44 0f 38 40 f3    	pmulld %xmm3,%xmm14
  400607:	66 41 0f 70 e9 aa    	pshufd $0xaa,%xmm9,%xmm5
  40060d:	66 0f 38 40 e9       	pmulld %xmm1,%xmm5
  400612:	66 41 0f 70 d9 ff    	pshufd $0xff,%xmm9,%xmm3
  400618:	66 0f 38 40 d8       	pmulld %xmm0,%xmm3
  40061d:	66 0f fe dd          	paddd  %xmm5,%xmm3
  400621:	66 41 0f fe dc       	paddd  %xmm12,%xmm3
  400626:	66 41 0f 70 ea 55    	pshufd $0x55,%xmm10,%xmm5
  40062c:	66 0f 38 40 ea       	pmulld %xmm2,%xmm5
  400631:	66 41 0f fe e8       	paddd  %xmm8,%xmm5
  400636:	66 41 0f 70 fd 55    	pshufd $0x55,%xmm13,%xmm7
  40063c:	66 0f 38 40 fa       	pmulld %xmm2,%xmm7
  400641:	66 41 0f 70 e7 55    	pshufd $0x55,%xmm15,%xmm4
  400647:	66 0f 38 40 e2       	pmulld %xmm2,%xmm4
  40064c:	66 41 0f 70 f2 aa    	pshufd $0xaa,%xmm10,%xmm6
  400652:	66 0f 38 40 f1       	pmulld %xmm1,%xmm6
  400657:	66 41 0f 70 d2 ff    	pshufd $0xff,%xmm10,%xmm2
  40065d:	66 0f 38 40 d0       	pmulld %xmm0,%xmm2
  400662:	66 0f fe d6          	paddd  %xmm6,%xmm2
  400666:	66 0f fe d5          	paddd  %xmm5,%xmm2
  40066a:	66 41 0f fe fb       	paddd  %xmm11,%xmm7
  40066f:	66 41 0f 70 ed aa    	pshufd $0xaa,%xmm13,%xmm5
  400675:	66 0f 38 40 e9       	pmulld %xmm1,%xmm5
  40067a:	66 41 0f 70 f7 aa    	pshufd $0xaa,%xmm15,%xmm6
  400680:	66 0f 38 40 f1       	pmulld %xmm1,%xmm6
  400685:	66 41 0f 70 cd ff    	pshufd $0xff,%xmm13,%xmm1
  40068b:	66 0f 38 40 c8       	pmulld %xmm0,%xmm1
  400690:	66 0f fe cd          	paddd  %xmm5,%xmm1
  400694:	66 0f fe cf          	paddd  %xmm7,%xmm1
  400698:	66 41 0f fe e6       	paddd  %xmm14,%xmm4
  40069d:	66 41 0f 70 ff ff    	pshufd $0xff,%xmm15,%xmm7
  4006a3:	66 0f 38 40 f8       	pmulld %xmm0,%xmm7
  4006a8:	66 0f fe fe          	paddd  %xmm6,%xmm7
  4006ac:	66 0f fe fc          	paddd  %xmm4,%xmm7
  4006b0:	66 0f 6f 05 c8 09 20 	movdqa 0x2009c8(%rip),%xmm0        # 601080 <data+0x40>
  4006b7:	00 
  4006b8:	66 0f 70 e0 aa       	pshufd $0xaa,%xmm0,%xmm4
  4006bd:	66 0f 70 e8 00       	pshufd $0x0,%xmm0,%xmm5
  4006c2:	ba e8 03 00 00       	mov    $0x3e8,%edx
  4006c7:	66 0f 6f c7          	movdqa %xmm7,%xmm0
  4006cb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  4006d0:	66 0f 6f f4          	movdqa %xmm4,%xmm6
  4006d4:	66 0f 66 f3          	pcmpgtd %xmm3,%xmm6
  4006d8:	66 0f fe f5          	paddd  %xmm5,%xmm6
  4006dc:	66 0f 38 40 f4       	pmulld %xmm4,%xmm6
  4006e1:	66 0f fa de          	psubd  %xmm6,%xmm3
  4006e5:	66 0f 6f f4          	movdqa %xmm4,%xmm6
  4006e9:	66 0f 66 f2          	pcmpgtd %xmm2,%xmm6
  4006ed:	66 0f fe f5          	paddd  %xmm5,%xmm6
  4006f1:	66 0f 38 40 f4       	pmulld %xmm4,%xmm6
  4006f6:	66 0f fa d6          	psubd  %xmm6,%xmm2
  4006fa:	66 0f 6f f4          	movdqa %xmm4,%xmm6
  4006fe:	66 0f 66 f1          	pcmpgtd %xmm1,%xmm6
  400702:	66 0f fe f5          	paddd  %xmm5,%xmm6
  400706:	66 0f 38 40 f4       	pmulld %xmm4,%xmm6
  40070b:	66 0f fa ce          	psubd  %xmm6,%xmm1
  40070f:	66 0f 6f f4          	movdqa %xmm4,%xmm6
  400713:	66 0f 66 f0          	pcmpgtd %xmm0,%xmm6
  400717:	66 0f fe f5          	paddd  %xmm5,%xmm6
  40071b:	66 0f 38 40 f4       	pmulld %xmm4,%xmm6
  400720:	66 0f fa c6          	psubd  %xmm6,%xmm0
  400724:	83 c2 ff             	add    $0xffffffff,%edx
  400727:	75 a7                	jne    4006d0 <main+0x160>
  400729:	48 83 c0 01          	add    $0x1,%rax
  40072d:	48 39 c8             	cmp    %rcx,%rax
  400730:	0f 85 6a fe ff ff    	jne    4005a0 <main+0x30>
  400736:	48 83 ec 18          	sub    $0x18,%rsp
  40073a:	66 0f 7f 1c 24       	movdqa %xmm3,(%rsp)
  40073f:	66 0f 7f 54 24 10    	movdqa %xmm2,0x10(%rsp)
  400745:	66 0f 7f 4c 24 20    	movdqa %xmm1,0x20(%rsp)
  40074b:	66 0f 7f 44 24 30    	movdqa %xmm0,0x30(%rsp)
  400751:	31 c0                	xor    %eax,%eax
  400753:	66 2e 0f 1f 84 00 00 	nopw   %cs:0x0(%rax,%rax,1)
  40075a:	00 00 00 
  40075d:	0f 1f 00             	nopl   (%rax)
  400760:	0f b6 0c 44          	movzbl (%rsp,%rax,2),%ecx
  400764:	30 88 90 10 60 00    	xor    %cl,0x601090(%rax)
  40076a:	0f b6 4c 44 01       	movzbl 0x1(%rsp,%rax,2),%ecx
  40076f:	30 88 91 10 60 00    	xor    %cl,0x601091(%rax)
  400775:	48 83 c0 02          	add    $0x2,%rax
  400779:	48 83 f8 20          	cmp    $0x20,%rax
  40077d:	75 e1                	jne    400760 <main+0x1f0>
  40077f:	be 54 08 40 00       	mov    $0x400854,%esi
  400784:	bf 01 00 00 00       	mov    $0x1,%edi
  400789:	ba 05 00 00 00       	mov    $0x5,%edx
  40078e:	31 c0                	xor    %eax,%eax
  400790:	e8 cb fc ff ff       	callq  400460 <write@plt>
  400795:	be 90 10 60 00       	mov    $0x601090,%esi
  40079a:	bf 01 00 00 00       	mov    $0x1,%edi
  40079f:	ba 20 00 00 00       	mov    $0x20,%edx
  4007a4:	31 c0                	xor    %eax,%eax
  4007a6:	e8 b5 fc ff ff       	callq  400460 <write@plt>
  4007ab:	be 5a 08 40 00       	mov    $0x40085a,%esi
  4007b0:	bf 01 00 00 00       	mov    $0x1,%edi
  4007b5:	ba 02 00 00 00       	mov    $0x2,%edx
  4007ba:	31 c0                	xor    %eax,%eax
  4007bc:	e8 9f fc ff ff       	callq  400460 <write@plt>
  4007c1:	31 ff                	xor    %edi,%edi
  4007c3:	e8 a8 fc ff ff       	callq  400470 <exit@plt>
  4007c8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  4007cf:	00 
```

The packed dword instructions (`pshufd`, `pmulld`, `paddd`, `psubd`) all perform their respective operaions on the DWORD (4-byte) components of each `xmm` register. That is, (for example), `paddd` is effectively doing four add operatitons - one each on the 4-byte chunks of the `xmm` registters. For our purposes, I treated each `xmm` as a 4-long integer array when doing my disassembly.

Speaking of, here is roughly the pseudocode I came up with for the main() function:

```
xmm0 = (0,0,0,1)
xmm1 = (0,0,1,0)
xmm2 = (0,1,0,0)
xmm3 = (1,0,0,0)

for i=0..1234567890123456789
  // these are done concurrently, not consecutively
  xmm0 := xmm0 * (10,10,10,10) + xmm1 * (f,f,f,f) + xmm2 * (e,e,e,e) + xmm3 * (d,d,d,d)
  xmm1 := xmm0 * (c,c,c,c) + xmm1 * (b,b,b,b) + xmm2 * (a,a,a,a) + xmm3 * (9,9,9,9)
  xmm2 := xmm0 * (8,8,8,8) + xmm1 * (7,7,7,7) + xmm2 * (6,6,6,6) + xmm3 * (5,5,5,5)
  xmm3 := xmm0 * (4,4,4,4) + xmm1 * (3,3,3,3) + xmm2 * (2,2,2,2) + xmm3 * (1,1,1,1)

  // actually inside a loop
  xmm0 = xmm0 % 0x0096433D
  xmm1 = xmm1 % 0x0096433D
  xmm2 = xmm2 % 0x0096433D
  xmm3 = xmm3 % 0x0096433D
```

The final result output of these registers is then XORed with data within the binary to give a flag.

## Matrix Multiplication

Simplifying the instructions above a bit, we can treat these operations as a larger 4x4 matrix. Furthermore, since we're just doing repeated multiplications, we effectively are raising the matrix to the 1234567890123456789 power. One technique for speeding up large exponentiation modulo a number is the square-and-multiply method. I wrote [a short script](./solutions/day10_solver.py) which gives the answer in a second or two instead of the long running time of the original program:

```
$ ./solver.py 
b'M4tr1x_3xp0n3nti4t1on_5728391723'
```
