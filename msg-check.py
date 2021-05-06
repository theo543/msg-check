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
path = re.sub(afterSlash, "bad-commit-message-blocker", os.path.realpath(sys.argv[0])) #supports symlinks

if os.path.isdir(path) == False:
    print("script folder not found, downloading...")
    os.system("git submodule update --init --recursive --force")
    if os.path.isdir(path) == False:
        print("download failed")
        exit(0)

path += "/bad-commit-message-blocker.py"

if os.path.exists(path) == False:
    print("script not found, downloading...")
    os.system("git submodule update --init --recursive --force")
    if os.path.exists(path) == False:
        print("download failed")
        exit(0)

proc = subprocess.run(args=["python", path, "--message", msg], capture_output=True, text=True)

#replace bright color codes with normal codes - git breaks bright codes for some reason
out = re.sub(colorCode, lambda match : str(int(match.group()) - 60), proc.stdout)

print(out)

if(proc.returncode == 1):
    print("\033[31mCheck failed, format message or use --no-verify\033[0m\n")
    exit(1)