import os

# Define paths
REPO_DIR = "/home/agent-lead/lexiflow-repo"
CITIES_DIR = os.path.join(REPO_DIR, "cities")
CITIES_HTML = os.path.join(REPO_DIR, "cities.html")

# Get all city files
city_files = sorted([f for f in os.listdir(CITIES_DIR) if f.endswith(".html")])

# Generate HTML for links
links = []
for filename in city_files:
    # city-name.html -> City Name
    city_name = filename.replace(".html", "").replace("-", " ").title()
    # Special cases for acronyms if any (e.g., St Louis -> St. Louis)
    if city_name == "St Louis": city_name = "St. Louis"
    
    link = f'<a href="/cities/{filename}" class="city-link">{city_name}</a>'
    links.append(link)

links_html = "".join(links)

# Read current cities.html
with open(CITIES_HTML, 'r') as f:
    content = f.read()

# Replace the grid content
# Finding <div class="city-grid"> ... </div>
start_tag = '<div class="city-grid">'
end_tag = '</div>'
start_idx = content.find(start_tag) + len(start_tag)
end_idx = content.find(end_tag, start_idx)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + "\n      " + links_html + "\n    " + content[end_idx:]
    
    with open(CITIES_HTML, 'w') as f:
        f.write(new_content)
    print(f"Updated {CITIES_HTML} with {len(links)} cities.")
else:
    print("Could not find city-grid div.")
