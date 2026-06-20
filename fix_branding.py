import os

ROOT = "/home/team/shared/LexiFlow-Final"

def replace_in_file(fpath, old_str, new_str):
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if old_str in content:
            new_content = content.replace(old_str, new_str)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error processing {fpath}: {e}")
    return False

updated_count = 0
for root, dirs, files in os.walk(ROOT):
    for name in files:
        if name.endswith(".html") or name.endswith(".js") or name.endswith(".py") or name.endswith(".md"):
            fpath = os.path.join(root, name)
            if replace_in_file(fpath, "LexiFlow Technologies Inc", "LexiFlow Technologies Inc"):
                updated_count += 1
                print(f"Updated: {fpath}")

print(f"Total files updated: {updated_count}")
