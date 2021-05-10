#!/usr/bin/env python

import sys
import subprocess
import re
import os

color_code = r"(?<=\033\[)9(?=[0-9])(?![0-9][0-9])"  # find 90-99 ansi codes (bright colors) and match only 9
comment_line = re.compile("^#.*\n?", re.MULTILINE)  # find comment lines
after_slash = r"[^/\\]+$"  # find last item in a path
get_slash = r"[/\\]"  # find slash

f = open(sys.argv[1], "r")
msg = re.sub(comment_line, "", f.read())  # remove comments
folder_path = re.sub(after_slash, "bad-commit-message-blocker", os.path.realpath(sys.argv[0]))  # supports symlinks
script_path = folder_path + re.search(get_slash, folder_path).group(0) + "bad_commit_message_blocker.py"

if msg == "":
    exit(0)  # do not check empty message

if not os.path.isdir(folder_path) or not os.path.exists(script_path):
    os.system("git submodule update --init --recursive --force")

proc = subprocess.run(args=["python", script_path, "--message", msg], capture_output=True, text=True)

# replace bright color codes with normal codes - git breaks bright codes for some reason
out = re.sub(color_code, "3", str(proc.stdout))

print(proc.stderr)  # report errors
print(out)

if proc.returncode == 1:
    print("\033[31mCheck failed, format message or use --no-verify\033[0m\n")
    exit(1)
