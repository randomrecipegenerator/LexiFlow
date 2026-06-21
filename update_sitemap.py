#!/usr/bin/env python3
"""Update sitemap.xml to use clean URLs and add missing pages."""
import re

SITEMAP_PATH = "/home/team/shared/LexiFlow-Final/sitemap.xml"

with open(SITEMAP_PATH, 'r') as f:
    content = f.read()

# Remove .html from all URLs
content = re.sub(r'\.html</loc>', '</loc>', content)

# Also fix the bad line 50 (missing changefreq attribute)
content = content.replace(
    '<lastmod>2026-06-22</lastmod><priority><priority>0.8</priority></url>',
    '<lastmod>2026-06-22</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>'
)

# Add missing pages (insert before </urlset>)
MISSING_PAGES = [
    ("/pricing", "0.9"),
    ("/signup", "0.8"),
    ("/login", "0.7"),
    ("/privacy", "0.5"),
    ("/terms", "0.5"),
    ("/soc2", "0.6"),
    ("/security", "0.6"),
    ("/meritscan", "0.9"),
    ("/integrations", "0.8"),
    ("/features", "0.8"),
    ("/san-francisco-medical-malpractice-intake", "0.8"),
    ("/ai-intake-agent", "0.9"),
    ("/personal-injury-software", "0.8"),
    ("/medical-chronology-software", "0.8"),
    ("/medical-chronology-template", "0.7"),
    ("/witness-testimony-analysis", "0.8"),
]

new_entries = ""
for page, priority in MISSING_PAGES:
    new_entries += f'   <url><loc>https://lexiflow.co{page}</loc><lastmod>2026-06-22</lastmod><changefreq>monthly</changefreq><priority>{priority}</priority></url>\n'

content = content.replace('</urlset>', new_entries + '</urlset>')

with open(SITEMAP_PATH, 'w') as f:
    f.write(content)

# Count URLs
url_count = content.count('<url>')
print(f"Updated sitemap: {url_count} URLs, .html extensions removed, new pages added")