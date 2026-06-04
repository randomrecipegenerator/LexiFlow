import os
import re

base_dir = '/home/team/shared/LexiFlow-Final'

# MAP OF OLD/INCORRECT LINKS TO NEW/CORRECT LINKS
LINK_MAP = {
    # State Ethics Guides
    r'/blog/state-ethics/ai-ethics-pennsylvania(?!\.html)': '/blog/pennsylvania-trial-lawyers-ai-ethics-legal-intake.html',
    r'/blog/state-ethics/ai-ethics-illinois(?!\.html)': '/blog/illinois-trial-lawyers-ai-ethics-legal-intake.html',
    r'/blog/state-ethics/ai-ethics-new-york(?!\.html)': '/blog/new-york-trial-lawyers-ai-ethics-legal-intake.html',
    r'/blog/state-ethics/ai-ethics-pennsylvania\.html': '/blog/pennsylvania-trial-lawyers-ai-ethics-legal-intake.html',
    r'/blog/state-ethics/ai-ethics-illinois\.html': '/blog/illinois-trial-lawyers-ai-ethics-legal-intake.html',
    r'/blog/state-ethics/ai-ethics-new-york\.html': '/blog/new-york-trial-lawyers-ai-ethics-legal-intake.html',
    
    # Other Blog Posts missing .html
    r'/blog/how-ai-medical-merit-review-cuts-case-screening(?!\.html)': '/blog/how-ai-medical-merit-review-cuts-case-screening.html',
    r'/blog/ethics-ai-legal-intake-responsible-implementation(?!\.html)': '/blog/ethics-ai-legal-intake-responsible-implementation.html',
    r'/blog/how-ai-medical-merit-review-slashes-law-firm-overhead(?!\.html)': '/blog/how-ai-medical-merit-review-slashes-law-firm-overhead.html',
    r'/blog/how-ai-medical-chronologies-revolutionizing-personal-injury-case-valuation(?!\.html)': '/blog/how-ai-medical-chronologies-revolutionizing-personal-injury-case-valuation.html',
    r'/blog/roi-ai-personal-injury-firms-scaling-without-adding-headcount(?!\.html)': '/blog/roi-ai-personal-injury-firms-scaling-without-adding-headcount.html',
    r'/blog/ai-vs-human-medical-chronology-accuracy(?!\.html)': '/blog/ai-vs-human-medical-chronology-accuracy.html',
}

def fix_links_in_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    new_content = content
    for pattern, replacement in LINK_MAP.items():
        # Ensure we match within href attributes
        new_content = re.sub(f'href="{pattern}"', f'href="{replacement}"', new_content)
        new_content = re.sub(f"href='{pattern}'", f"href='{replacement}'", new_content)

    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    return False

count = 0
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.html'):
            if fix_links_in_file(os.path.join(root, file)):
                count += 1

print(f"Fixed links in {count} files.")
