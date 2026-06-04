import os
from datetime import datetime

BASE_URL = "https://lexiflow.co" # Updating to .ai as per user's enterprise preference
CORE_PAGES = [
    "index.html", "features.html", "solutions.html", "roi-calculator.html", 
    "dashboard.html", "portal.html", "usa-cities/index.html", "whitepaper.html", 
    "privacy.html", "terms.html", "depolens.html", "meritscan.html"
]

def generate_sitemap():
    sitemap_path = "/home/team/shared/lexiflow-pro/sitemap.xml"
    today = datetime.now().strftime("%Y-%m-%d")
    
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Add Core Pages
    for page in CORE_PAGES:
        loc = f"{BASE_URL}/{page}" if page != "index.html" else f"{BASE_URL}/"
        priority = "1.0" if page == "index.html" else "0.8"
        xml.append(f'   <url><loc>{loc}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq><priority>{priority}</priority></url>')
    
    # Add City Pages
    city_dir = "/home/team/shared/lexiflow-pro/usa-cities"
    if os.path.exists(city_dir):
        for filename in sorted(os.listdir(city_dir)):
            if filename.endswith(".html"):
                loc = f"{BASE_URL}/locations/{filename}"
                xml.append(f'   <url><loc>{loc}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>')
    
    xml.append('</urlset>')
    
    with open(sitemap_path, "w") as f:
        f.write("\n".join(xml))
    
    print(f"Sitemap updated at {sitemap_path} with core and city pages.")

if __name__ == "__main__":
    generate_sitemap()
