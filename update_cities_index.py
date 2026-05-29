import os

def update_cities_html():
    city_dir = "/home/team/shared/lexiflow-mvp/cities"
    cities = []
    if os.path.exists(city_dir):
        for filename in sorted(os.listdir(city_dir)):
            if filename.endswith(".html"):
                slug = filename.replace(".html", "")
                name = slug.replace("-", " ").title()
                # Special cases for names like "St. Louis" which might be "St.-Louis" in slug
                cities.append((name, filename))
    
    links_html = ""
    for name, filename in cities:
        links_html += f'            <a href="/cities/{filename}" class="city-link">{name}</a>\n'
    
    path = "/home/team/shared/lexiflow-mvp/cities.html"
    with open(path, "r") as f:
        content = f.read()
    
    import re
    # Replace the content inside <div class="city-grid" id="city-list"> ... </div>
    pattern = r'(<div class="city-grid" id="city-list">).*?(</div>)'
    new_content = re.sub(pattern, r'\1\n' + links_html + r'        \2', content, flags=re.DOTALL)
    
    with open(path, "w") as f:
        f.write(new_content)
    print(f"Updated {path} with {len(cities)} cities.")

if __name__ == "__main__":
    update_cities_html()
