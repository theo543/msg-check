#!/usr/bin/env python
import configparser
import os
import re
import subprocess
import sys

DEFAULT_CONFIG = {
    'arguments': {'body': '72', 'subject': '50'},
    'rules': {str(nr): '1' for nr in range(1, 7)},
    'core': {'just-warn': '1'}
}


def main():
    # compute paths
    py_file = os.path.realpath(sys.argv[0])  # supports symlinks
    py_folder = re.sub(r"[^/\\]+$", "", py_file)
    bcmb_path = py_folder + "bad-commit-message-blocker" + py_folder[-1] + "bad_commit_message_blocker.py"
    config_path = py_folder + "msg-check-config.ini"

    msg = cleanup_message(open(sys.argv[1], "r").read())  # remove comments

    parser = configparser.ConfigParser()

    try:
        parser.read(config_path)
        if repair_config(parser):
            parser.write(open(config_path, "w"))
            print("Invalid/missing config data reset")
    except (FileNotFoundError, configparser.Error):
        parser = configparser.ConfigParser()  # reset parser
        parser.read_dict(DEFAULT_CONFIG)
        parser.write(open(config_path, "w"))  # reset config file
        print("Invalid/missing config file reset")

    if re.match(r"^[\n ]*$", msg):
        exit(0)  # do not check empty message

    if not os.path.isfile(bcmb_path):
        os.system("git submodule update --init --recursive --force")
        if not os.path.isfile(bcmb_path):
            print("Failed to download bad-commit-message-blocker submodule")
            exit(0)

    proc = subprocess.run(
        args=["python", bcmb_path, "--message", msg, "--subject-limit", parser['arguments']['subject'], "--body-limit",
              parser['arguments']['body']], capture_output=True, text=True)

    # replace bright color codes with normal codes - git breaks bright codes for some reason
    # regex matches a 9 preceded by \033 and followed by only one other digit
    out = re.sub(r"(?<=\033\[)9(?=[0-9])(?![0-9][0-9])", "3", str(proc.stdout))
    out = out.split('\n')[-9:-1]
    out, block_commit = parse_rules(out, parser['rules'])
    print(proc.stderr)  # report errors
    print('\n'.join(out))
    if block_commit:
        if int(parser['core']['just-warn']) != 0:
            print("\033[33mCheck failed, consider amending\033[0m")
            exit(0)
        else:
            print("\033[31mCheck failed, format message or use --no-verify\033[0m")
            print("Your message was:")
            print(msg)
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
    # replicate git message cleanup:
    s = re.sub(re.compile(r"^#.*\n?", re.MULTILINE), "", s)  # remove comments
    s = s.strip('\n')  # remove trailing newlines
    # does not support commits with --message if you try to start the message with #
    # so don't start with #
    # example: don't use "#23 fix issue", use "Fix issue #23"
    return s


def parse_rules(s, r):
    fail = False
    for i in range(1, 7):
        if int(r[str(i)]) == 0:
            s[i] = re.sub("(PASSED|FAILED)", "\033[34m\\1", s[i])  # change color to blue
        else:
            fail |= "FAILED" in s[i]
    return s, fail


if __name__ == "__main__":
    main()
