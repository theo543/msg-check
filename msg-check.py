#!/usr/bin/env python

import sys
import subprocess
import re
import os

colorCode = r"(?<=\033\[)9[0-9](?![0-9])" #find 90-99 ansi codes (bright colors)
commentLine = re.compile("^#.*\n?", re.MULTILINE) #find comment lines
afterSlash = r"[^\/\\]+$" #find last item in a path

f = open(sys.argv[1], "r")
msg = re.sub(commentLine, "", f.read()) #remove comments
path = re.sub(afterSlash, "bad-commit-message-blocker/bad_commit_message_blocker.py", os.path.realpath(sys.argv[0])) #supports symlinks

proc = subprocess.run(args=["python", path, "--message", msg], capture_output=True, text=True)

#replace bright color codes with normal codes - git breaks bright codes for some reason
out = re.sub(colorCode, lambda match : str(int(match.group()) - 60), proc.stdout)

print(out)

if(proc.returncode == 1):
    print("\033[31mCheck failed, format message or use --no-verify\033[0m\n")
    exit(1)