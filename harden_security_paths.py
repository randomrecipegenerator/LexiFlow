import os
import re

def harden_paths(file_path, depth=1):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Prefix for relative paths
    prefix = "../" * depth

    # Replace relative links that start with ./ (but not within text)
    # We want to catch href="./", src="./", etc.
    content = content.replace('href="./', f'href="{prefix}')
    content = content.replace('src="./', f'src="{prefix}')
    
    # Special case for the logo or links that were already fixed if any (but here they are ./ because it's a copy)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    harden_paths("/home/team/shared/LexiFlow-Final/hardened-suite/security.html", depth=1)
    print("Hardened paths in hardened-suite/security.html")
