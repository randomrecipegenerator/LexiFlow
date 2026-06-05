import subprocess
import os

os.chdir("/home/team/shared/LexiFlow-Final")
cmds = [
    ["git", "add", "."],
    ["git", "commit", "-m", "fix: restore Dashboard link to navigation and sync all pages"],
    ["git", "push", "origin", "main"]
]

for cmd in cmds:
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
