import os
import re

base_dir = '/home/team/shared/LexiFlow-Final'
cities_file = os.path.join(base_dir, 'cities.html')

# Map filename to relative path in locations
mapping = {}
locations_dir = os.path.join(base_dir, 'locations')

for root, dirs, files in os.walk(locations_dir):
    for f in files:
        if f.endswith('.html'):
            rel_path = os.path.relpath(os.path.join(root, f), base_dir)
            mapping[f] = rel_path

with open(cities_file, 'r') as f:
    content = f.read()

def replace_link(match):
    original_path = match.group(1)
    filename = os.path.basename(original_path)
    if filename in mapping:
        return f'href="/{mapping[filename]}"'
    return match.group(0)

# Replace href="/locations/city.html" with the correct path
new_content = re.sub(r'href="/locations/([^"]+)"', replace_link, content)

# Also replace any other occurrences of /locations/
new_content = new_content.replace('/locations/', '/locations/')

with open(cities_file, 'w') as f:
    f.write(new_content)

print("Updated links in cities.html")
