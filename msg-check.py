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


def main():
    # compute paths
    py_file = os.path.realpath(sys.argv[0])  # supports symlinks
    py_folder = re.sub(r"[^/\\]+$", "", py_file)
    bcmb_folder = py_folder + "bad-commit-message-blocker"
    bcmb_path = bcmb_folder + re.search(r"[/\\]", py_file).group() + "bad_commit_message_blocker.py"
    config_path = py_folder + "msg-check-config.ini"

    msg = cleanup_message(open(sys.argv[1], "r").read())  # remove comments

    parser = configparser.ConfigParser()

    try:
        parser.read(config_path)
        if repair_config(parser):
            parser.write(open(config_path, "w"))
            print("Invalid/missing config data reset")
    except (FileNotFoundError, configparser.Error) as e:
        parser = configparser.ConfigParser()  # reset parser
        parser.read_dict(DEFAULT_CONFIG)
        parser.write(open(config_path, "w"))  # reset config file
        print("Invalid/missing config file reset")

    if re.match(r"^[\n ]*$", msg):
        exit(0)  # do not check empty message

    if not os.path.isdir(bcmb_folder) or not os.path.exists(bcmb_path):
        os.system("git submodule update --init --recursive --force")

    proc = subprocess.run(
        args=["python", bcmb_path, "--message", msg, "--subject-limit", parser['arguments']['subject'], "--body-limit",
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


def repair_config(p: configparser):
    change = False
    for s, a in DEFAULT_CONFIG.items():
        if not p.has_section(s):
            p.add_section(s)
        for o in a:
            if not (p.has_option(s, o) and re.fullmatch("[0-9]*", p[s][o])):
                p[s][o] = DEFAULT_CONFIG[s][o]
                change = True
    return change


def cleanup_message(s: str):
    s = re.sub(re.compile("^#.*\n?", re.MULTILINE), "", s)
    # does not support commits with --message if any line starts with "#"
    # so don't start lines with '#'
    # instead of "#23 fix" use "Fix #23"
    return s


if __name__ == "__main__":
    main()
