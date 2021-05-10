#!/usr/bin/env python

import configparser
import os
import re
import subprocess
import sys

default_config = {
    'arguments': {'body': '72', 'subject': '50'},
    'rules': {str(nr): '1' for nr in range(1, 7)}
}
parser = configparser.ConfigParser()
color_code = r"(?<=\033\[)9(?=[0-9])(?![0-9][0-9])"  # find 90-99 ansi codes (bright colors) and match only 9
comment_line = re.compile("^#.*\n?", re.MULTILINE)  # find comment lines
after_slash = r"[^/\\]+$"  # find last item in a path
get_slash = r"[/\\]"  # find slash

f = open(sys.argv[1], "r")
msg = re.sub(comment_line, "", f.read())  # remove comments
folder_path = re.sub(after_slash, "bad-commit-message-blocker", os.path.realpath(sys.argv[0]))  # supports symlinks
slash = re.search(get_slash, folder_path).group(0)
script_path = folder_path + slash + "bad_commit_message_blocker.py"
config_path = re.sub(after_slash, "msg-check-config.ini", os.path.realpath(sys.argv[0]))

try:
    parser.read(config_path)
except (FileNotFoundError, configparser.Error) as e:
    parser = configparser.ConfigParser()  # reset parser
    cfg = open(config_path, "w")
    parser.read_dict(default_config)
    parser.write(cfg)  # reset config file
    print("Error reading config, config reset.")

# validate config
changed = False
for section, properties in default_config.items():
    if not parser.has_section(section):
        parser.add_section(section)
    for val in properties:
        if not(parser.has_option(section, val) and re.fullmatch("[0-9]*", parser[section][val])):
            parser[section][val] = default_config[section][val]
            changed = True
if changed:
    parser.write(open(config_path, "w"))
    print("Missing/invalid config values reset.")

if msg == "":
    exit(0)  # do not check empty message

if not os.path.isdir(folder_path) or not os.path.exists(script_path):
    os.system("git submodule update --init --recursive --force")

proc = subprocess.run(
    args=["python", script_path, "--message", msg, "--subject-limit", parser['arguments']['subject'], "--body-limit",
          parser['arguments']['body']], capture_output=True, text=True)

# replace bright color codes with normal codes - git breaks bright codes for some reason
out = re.sub(color_code, "3", str(proc.stdout))

out = out.split('\n')
block_commit = False
i = 1
while i < 6:
    j = len(out) - 9 + i
    if parser['rules'][str(i)] == '0':
        out[j] = re.sub("(PASSED|FAILED)", "\033[34m\\1", out[j])  # change color to blue
    else:
        block_commit |= "FAILED" in out[j]
    i += 1
out = '\n'.join(out)

print(proc.stderr)  # report errors
print(out)

if block_commit:
    print("\033[31mCheck failed, format message or use --no-verify\033[0m\n")
    exit(1)
