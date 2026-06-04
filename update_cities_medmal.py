import os
import glob

base_dir = '/home/team/shared/LexiFlow-Final'
cities_file = os.path.join(base_dir, 'cities.html')

# 1. Collect all medmal pages
medmal_pages = []
for html_path in glob.glob(os.path.join(base_dir, 'locations', '**', 'medmal-*.html'), recursive=True):
    rel_path = os.path.relpath(html_path, base_dir)
    filename = os.path.basename(html_path)
    # e.g. medmal-philadelphia.html -> Philadelphia
    city_name = filename.replace('medmal-', '').replace('.html', '').replace('-', ' ').title()
    if city_name == 'Nyc': city_name = 'New York City'
    if city_name == 'La': city_name = 'Los Angeles'
    
    medmal_pages.append({'name': city_name, 'path': '/' + rel_path})

medmal_pages.sort(key=lambda x: x['name'])

# 2. Generate the medmal grid HTML
medmal_grid_html = ""
for page in medmal_pages:
    medmal_grid_html += f'            <a href="{page["path"]}" class="city-link" style="border-color: #ef4444; background: #fef2f2;">{page["name"]} (MedMal)</a>\n'

# 3. Read cities.html and inject the section
with open(cities_file, 'r') as f:
    content = f.read()

# Inject before the main city list
insertion_point = '<div class="city-grid">'
special_section = f"""
    <div style="margin-top: 40px; padding: 40px; background: #fff; border: 1px solid #e2e8f0; border-radius: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <h2 style="font-family: 'Playfair Display', serif; font-size: 28px; margin-bottom: 12px; color: #0f172a;">AI Medical Merit Review Markets</h2>
        <p style="color: #64748b; margin-bottom: 32px;">Specialized MeritScan™ intake for high-stakes Medical Malpractice and Surgical Error litigation.</p>
        <div class="city-grid" style="padding: 0; margin-bottom: 0;">
{medmal_grid_html}
        </div>
    </div>
    
    <h2 style="font-family: 'Playfair Display', serif; font-size: 28px; margin-top: 64px; margin-bottom: 12px; color: #0f172a;">National Personal Injury Intake Network</h2>
"""

new_content = content.replace(insertion_point, special_section + insertion_point)

with open(cities_file, 'w') as f:
    f.write(new_content)

print(f"Added {len(medmal_pages)} specialized medmal links to cities.html")
