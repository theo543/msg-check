This script is a commit message hook that automatically
runs [bad-commit-message-blocker](https://github.com/platisd/bad-commit-message-blocker). I wrote this script to use as
a global hook to check all my commit messages.

## Configuration

Use the arguments section in msg-check-config.ini (generated when the script is run) to modify the subject and body
length limits.

Use the rules section to disable rules. Disabled rules will be shown in blue and will not block commits.

Switch just-warn off to block commits instead of suggesting amending.

Delete the file to restore defaults.

## Installation

Run the symlink script for your OS and move commit-msg to your hooks folder (recommended for easy updating).
Alternatively, you could copy the script files to your hooks folder and rename the script "commit-msg".

Git does not support multiple hooks of the same type. If you already have global or local commit message hooks, you can
run msg-check from your hooks.

## Dependencies

Python 3

`pip install textblob`

`python -m textblob.download_corpora`

## Enabling Symlinks on Windows

Git for Windows may break symlinks. This is because admin access is required to create symlinks. Git may delete symlinks
when running some commands and won't be able to recreate them. To allow any user to create symlinks, turn on Developer
Mode in the Settings app. You may also need to run the following commands to inform Git that symlinks are now enabled
and/or restart your computer:

```
git config --local core.symlinks true
git config --global core.symlinks true
git config --system core.symlinks true
```

This will enable Git symlinks on your PC.

If you keep your hooks in a repository (or use symlinks in any other repo), you should either do this or gitignore the
links.

## Recommendations

Since GitHub caps titles at 72 characters, you should set your max subject length to 72. No reason to keep it at 50.

You could increase the body length to 80-120 if you want. Just make sure your messages are readable without
auto-wrapping.

If you commit from your IDE or from a Git GUI tool, it may have built-in commit autoformatting/warning options.
