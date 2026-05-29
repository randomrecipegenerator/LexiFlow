import os
import re

def verify_links():
    project_root = "/home/team/shared/lexiflow-mvp"
    cities_html_path = os.path.join(project_root, "cities.html")
    cities_dir = os.path.join(project_root, "cities")
    
    with open(cities_html_path, "r") as f:
        content = f.read()
    
    # Extract all hrefs starting with /cities/
    links = re.findall(r'href="/cities/([^"]+)"', content)
    
    missing = []
    for link in links:
        file_path = os.path.join(cities_dir, link)
        if not os.path.exists(file_path):
            missing.append(link)
            
    if missing:
        print(f"FAILED: {len(missing)} links are missing files!")
        for m in missing[:10]:
            print(f" - Missing: {m}")
    else:
        print(f"SUCCESS: All {len(links)} links in cities.html verified against file system.")

if __name__ == "__main__":
    verify_links()
