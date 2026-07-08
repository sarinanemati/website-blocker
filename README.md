# website-blocker
a website blocker using python to block distracting website while you're working/studying
## features
### 1. system blocking 
### 2. smart timing = 9 AM to 5PM from monday to friday (default)
### 3. cross platform = for windows,mac,linux OS
### 4. statistics 
### 5. many options for blocking = force block and authomatic block

## libraries
### os, tkinter, datetime, time, subprocess, platform, path, json, sys, and the optional one for windows: ctypes, it was lazy import and if it was mac or linux it will ignore that and we are safe

## how it works
### the user will face a menu and 8 options to choose
1. worktime block for 9AM to 5PM and workday
2. force blocking regardless of time
3. unblocking
4. statistics
5.configure work hours
6. flush DNS
7. list of blocked websites
8. exiting

after chossing blocking options computer will check host file and redirects to localhost and ther website fails to load because it got blocked.

contributions are also welcome.
improvment idea:
an app for productivity by blocking apps and websites for more focus
