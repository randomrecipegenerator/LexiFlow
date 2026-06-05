import os
import subprocess

path = "/home/team/shared/LexiFlow-Final/standardize_nav_footer.py"
print(f"Running {path}")
result = subprocess.run(["python3", path], capture_output=True, text=True)
with open("/home/team/shared/sweep_log.txt", "w") as f:
    f.write(result.stdout)
    f.write(result.stderr)
print("Done")
