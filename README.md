This script is a commit message hook that automatically runs [bad-commit-message-blocker](https://github.com/platisd/bad-commit-message-blocker).
I wrote this script to use as a global hook to check all my commit messages.

# Installation

Run the symlink script for your OS and move commit-msg to your hooks folder.

Alternatively, you could copy the script and the submodule to your hooks folder and rename the script "commit-msg".

Git does not support multiple hooks of the same type. If you already have global or local commit message hooks, you can run msg-check from your hooks.

If the bad-commit-message-blocker folder or script is missing the hook will download it.
