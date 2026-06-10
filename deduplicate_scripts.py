import os
import re

def deduplicate_scripts(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all occurrences of the script tag
                pattern = r'<script src=".*?shared-layout\.js"></script>'
                matches = list(re.finditer(pattern, content))
                
                if len(matches) > 1:
                    print(f"Deduplicating {filepath}")
                    # Keep only the last one
                    last_match = matches[-1]
                    new_content = content[:last_match.start()]
                    new_content = re.sub(pattern, '', new_content)
                    new_content += content[last_match.start():]
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == "__main__":
    deduplicate_scripts("/home/team/shared/LexiFlow-Final")
    print("Deduplication complete.")
