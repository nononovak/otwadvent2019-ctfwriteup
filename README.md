# OverTheWire Advent Bonanza 2019 Writeup

Enclosed is my writeup for the 2019 OTW Advent CTF (https://advent2019.overthewire.org). This year I played under the team name Speculatores. There was a pretty nice selection of problems this year. While I was stymied by a couple different challenges, I felt like I made progress or solved each of the problems presented.

## Scoring

The final competition results can be found [here](https://advent2019.overthewire.org/dashboard/scoreboard/). Points allocated were dynamic this year so their value depended on how many total solves there were in the competition. Personally, I perfer this method - mostly because sometimes problem creators don't quite assess the difficulty of each problem ahead of time (harder _or_ easier).

## Problems

1. Santaty Flag - __SOLVED__: Was in the Discord channel topic `AOTW{Testing123}`
2. [Challenge Zero - re, crypto](./day0_challenge_zero.md) - __SOLVED__: steg in ASCII art, then x86 disassembly - AES decryption recover the flag
3. [Easter Egg 1 - fun](./easter_eggs.md) - __SOLVED*__: Navigate from `/robots.txt~`
4. [Day 1 - 7110 - keylogger, programming](./day1_7110.md) - __SOLVED__: 
5. [Day 2 - Summer ADVENTure - crypto, rev, network, misc](./day2_summer_adventure.md) - __SOLVED__: 
6. [Day 3 - Northpole Airwaves - forensics, gnuradio](./day3_northpole_airwaves.md) - __SOLVED*__: 
7. [Day 4 - mooo - web](./day4_mooo.md) - __SOLVED__:
8. [Easter Egg 2 - fun](./easter_eggs.md) - __SOLVED__: `X-EasterEgg2` header on several pages
9. [Day 5 - Sudo Sudoku - misc, sudoku](./day5_sudo_sudoku.md) - __SOLVED__: 
10. [Day 6 - Genetic Mutation - pwn, misc](./day6_genetic_mutation.md) - __SOLVED__: 
11. [Day 7 - Naughty or Nice V2 - pwn, crypto](./day7_naughty_or_nice_v2.md) - __SOLVED__: 
12. [Day 8 - Unmanaged - pwn, dotnet](./day8_unmanaged.md) - __NOT SOLVED__: 
13. [Day 9 - GrinchNet - re, crypto](./day9_grinchnet.md) - __SOLVED__: 
14. [Easter Egg 3 - fun](./easter_eggs.md) - __SOLVED*__: Aztec code inside a QR code in an image on Twitter
15. [Day 10 - ChristmaSSE KeyGen - rev, math](./day10_christmasse_keygen.md) - __SOLVED__: 
16. [Day 11 - Heap Playground - pwn, heap](./day11_heap_playground.md) - __SOLVED__: 
17. [Day 12 - Naughty List - web](./day12_naughty_list.md) - __SOLVED*__: Encryption and decryption oracles with a TOCTOU transfer bug
18. [Day 13 - Cookie Codebook team Brain/Brawn - fun](https://github.com/OverTheWireOrg/advent2019-cookiescodebook): fun challenge, see the link
19. [Day 14 - tiny runes - game, reversing, asset files](./day14_tiny_runes.md) - __SOLVED__: 
20. [Day 15 - Self-Replicating Toy - rev](./day15_self_replicating_toy.md) - __SOLVED__: 
21. [Day 16 - Musical Stegano - steganography](./day16_musical_stegano.md) - __SOLVED__: 
22. [Day 17 - Snowflake Idle - web, crypto](./day17_snowflake_idle.md) - __SOLVED__: 
23. [Day 18 - Impressive Sudoku - pwn, math](./day18_impressive_sudoku.md) - __SOLVED__: Arbitrary write primitive to set a GOT address and solving math equation constraints
24. [Day 19 - Santa's Signature - crypto](./day19_santas_signature.md) - __SOLVED__: Broken RSA signature scheme
25. [Day 20 - Our Hearts, Strike a pose - fun](https://github.com/OverTheWireOrg/advent2019-strikeapose): fun challenge, see the link
26. [Days 21-22 - Battle of the Galaxies - battle](./day21_battle.md) - __PLAYED__: Competitive AIvAI matchups using a structured game
27. Day 22 - Survey - misc: End of CTF survey (overlapping with "Battle" day) which awarded a flag 
28. [Day 23 - Gr8 Escape - pwn](./day23_gr8_escape.md) - __SOLVED__: Statically compiled "game" program which overwrote a function pointer, leading to a stack overwrite/leak which gave a shell with ROP
29. [Day 24 - Got shell? - web, linux](./day24_got_shell.md) - __SOLVED__: Linux pipe and command-line fu to solve a "captcha"
30. [Day 25 - Lost in Maze - misc, pwned!](./day25_lost_in_maze.md) - __SOLVED__: Maze solver in ASCII art

__SOLVED*__ are written up, but as the writeup describes I only completed these with help after the competition was over.