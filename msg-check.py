#!/usr/bin/env python

import configparser
import os
import re
import subprocess
import sys

DEFAULT_CONFIG = {
    'arguments': {'body': '72', 'subject': '50'},
    'rules': {str(nr): '1' for nr in range(1, 7)}
}
AFTER_SLASH = r"[^/\\]+$"  # find last item in a path

parser = configparser.ConfigParser()
f = open(sys.argv[1], "r")
msg = re.sub(re.compile("^#.*\n?", re.MULTILINE), "", f.read())  # remove comments
folder_path = re.sub(AFTER_SLASH, "bad-commit-message-blocker", os.path.realpath(sys.argv[0]))  # supports symlinks
slash = re.search(r"[/\\]", folder_path).group(0)
script_path = folder_path + slash + "bad_commit_message_blocker.py"
config_path = re.sub(AFTER_SLASH, "msg-check-config.ini", os.path.realpath(sys.argv[0]))

try:
    parser.read(config_path)
except (FileNotFoundError, configparser.Error) as e:
    parser = configparser.ConfigParser()  # reset parser
    cfg = open(config_path, "w")
    parser.read_dict(DEFAULT_CONFIG)
    parser.write(cfg)  # reset config file
    print("Error reading config, config reset.")

# validate config
changed = False
for section, properties in DEFAULT_CONFIG.items():
    if not parser.has_section(section):
        parser.add_section(section)
    for val in properties:
        if not(parser.has_option(section, val) and re.fullmatch("[0-9]*", parser[section][val])):
            parser[section][val] = DEFAULT_CONFIG[section][val]
            changed = True
if changed:
    parser.write(open(config_path, "w"))
    print("Missing/invalid config values reset.")

if re.match(r"^[\n ]*$", msg):
    exit(0)  # do not check empty message

if not os.path.isdir(folder_path) or not os.path.exists(script_path):
    os.system("git submodule update --init --recursive --force")

proc = subprocess.run(
    args=["python", script_path, "--message", msg, "--subject-limit", parser['arguments']['subject'], "--body-limit",
          parser['arguments']['body']], capture_output=True, text=True)

# replace bright color codes with normal codes - git breaks bright codes for some reason
# regex matches a 9 preceded by \033 and followed by only one other digit
out = re.sub(r"(?<=\033\[)9(?=[0-9])(?![0-9][0-9])", "3", str(proc.stdout))

out = out.split('\n')
block_commit = False
i = 1
while i <= 6:
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
