import os
import glob

base_dir = '/home/team/shared/LexiFlow-Final'
locations_dir = os.path.join(base_dir, 'locations')

# DESIGN SYSTEM
HEADER = """<nav><div class="nav-container">
    <a href="/" class="logo"><span>LF</span> LexiFlow</a>
    <ul class="nav-links" id="navLinks">
      <li><a href="/dashboard.html">Dashboard</a></li>
      <li><a href="/pricing.html">Pricing</a></li>
      <li><a href="/blog.html">Blog</a></li>
      <li><a href="/cities.html">Areas We Serve</a></li>
      <li><a href="/pricing.html" class="btn-cta">Get Started</a></li>
    </ul>
    <button class="nav-toggle" onclick="document.getElementById('navLinks').classList.toggle('active')">☰</button>
  </div></nav>"""

FOOTER = """<footer>
    <div class="footer-container">
      <div class="footer-col">
        <a href="/" class="footer-logo">LexiFlow</a>
        <p>Enterprise-grade AI for legal intake and lead qualification. Built for the modern attorney.</p>
      </div>
      <div class="footer-col">
        <h4>Products</h4>
        <ul>
          <li><a href="/ai-intake-agent.html">LexiFlow Intake</a></li>
          <li><a href="/voice-ai-receptionist.html">Voice AI</a></li>
          <li><a href="/ai-medical-chronologies.html">Medical Review</a></li>
          <li><a href="/auto-document-drafter.html">Doc Automation</a></li>
          <li><a href="/depolens-ai.html">DepoLens AI</a></li>
          <li><a href="/settlement-estimator.html">Settlement AI</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Legal</h4>
        <ul>
          <li><a href="/privacy.html">Privacy Policy</a></li>
          <li><a href="/terms.html">Terms of Service</a></li>
          <li><a href="#">SOC2 Compliance</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Security</h4>
        <div style="font-size: 24px; display: flex; gap: 16px;">
          <i class="bi bi-shield-lock"></i>
          <i class="bi bi-safe"></i>
          <i class="bi bi-fingerprint"></i>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      &copy; 2026 LexiFlow AI. All rights reserved.
    </div>
  </footer>"""

STYLE = """
    :root {
      --navy: #0f172a; --gold: #c9a84c; --gold-light: #e2c96e;
      --slate-50: #f8fafc; --slate-100: #f1f5f9; --slate-200: #e2e8f0; --slate-400: #94a3b8; --slate-600: #475569;
      --slate-900: #0f172a; --max-width: 1200px;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; background: #fff; color: var(--slate-900); line-height: 1.6; padding-top: 80px; }
    
    nav { position: fixed; top: 0; width: 100%; height: 80px; background: rgba(255,255,255,0.98); border-bottom: 1px solid var(--slate-200); z-index: 1000; display: flex; align-items: center; }
    .nav-container { max-width: var(--max-width); margin: 0 auto; width: 100%; padding: 0 40px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: var(--navy); text-decoration: none; display: flex; align-items: center; gap: 12px; }
    .logo span { background: var(--navy); color: var(--gold); padding: 4px 8px; border-radius: 4px; font-size: 18px; }
    .nav-links { display: flex; gap: 32px; list-style: none; }
    .nav-links a { text-decoration: none; color: var(--slate-600); font-weight: 500; font-size: 15px; }
    .nav-links a:hover { color: var(--navy); }
    .btn-cta { background: var(--gold); color: var(--navy); padding: 12px 24px; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 14px; }
    .nav-toggle { display: none; background: none; border: none; font-size: 24px; cursor: pointer; color: var(--navy); }

    .hero { padding: 100px 0 60px; background: radial-gradient(40% 40% at 50% 0%, rgba(201, 168, 76, 0.05) 0%, transparent 100%); text-align: center; }
    .max-w-screen { max-width: var(--max-width); margin: 0 auto; padding: 0 40px; }
    .hero h1 { font-family: 'Playfair Display', serif; font-size: 56px; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 24px; line-height: 1.1; color: var(--navy); }
    .hero h1 span { color: var(--gold); }
    .hero p { font-size: 20px; color: var(--slate-600); max-width: 700px; margin: 0 auto; line-height: 1.6; }

    .city-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; padding: 40px 0; }
    .city-link { display: block; padding: 16px; background: var(--slate-50); border: 1px solid var(--slate-200); border-radius: 12px; font-weight: 600; text-decoration: none; color: var(--navy); transition: all 0.2s ease; text-align: center; font-size: 14px; }
    .city-link:hover { border-color: var(--gold); background: white; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); transform: translateY(-3px); color: var(--gold); }

    .ethics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-top: 32px; }
    .ethics-card { display: block; padding: 32px; background: white; border: 1px solid var(--slate-200); border-radius: 24px; text-decoration: none; transition: all 0.2s; }
    .ethics-card:hover { border-color: var(--gold); transform: translateY(-4px); box-shadow: 0 20px 40px -10px rgba(0,0,0,0.05); }
    .ethics-card h4 { color: var(--navy); font-size: 20px; margin-bottom: 12px; font-family: 'Playfair Display', serif; }
    .ethics-card p { color: var(--slate-600); font-size: 15px; line-height: 1.6; }

    footer { background: var(--navy); color: var(--slate-400); padding: 80px 0 40px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 100px; }
    .footer-container { max-width: var(--max-width); margin: 0 auto; padding: 0 40px; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; }
    .footer-logo { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: #fff; text-decoration: none; margin-bottom: 20px; display: block; }
    .footer-col h4 { color: #fff; margin-bottom: 20px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em; }
    .footer-col ul { list-style: none; }
    .footer-col ul li { margin-bottom: 12px; }
    .footer-col ul a { color: var(--slate-400); text-decoration: none; font-size: 14px; }
    .footer-col ul a:hover { color: var(--gold); }
    .footer-bottom { max-width: var(--max-width); margin: 60px auto 0; padding: 40px 40px 0; border-top: 1px solid rgba(255,255,255,0.1); font-size: 13px; text-align: center; }

    @media (max-width: 768px) {
      .nav-container { padding: 0 20px; }
      .nav-links { display: none; position: absolute; top: 80px; left: 0; width: 100%; background: #fff; flex-direction: column; padding: 20px; gap: 20px; border-bottom: 1px solid var(--slate-200); box-shadow: 0 10px 15px rgba(0,0,0,0.05); }
      .nav-links.active { display: flex; }
      .nav-toggle { display: block; }
      .btn-cta { display: none; }
      .hero h1 { font-size: 36px; }
      .footer-container { grid-template-columns: 1fr; gap: 40px; text-align: center; }
      .city-grid { grid-template-columns: 1fr; }
    }
"""

ETHICS_SECTION = """
<section style="background: var(--slate-50); padding: 80px 0; border-top: 1px solid var(--slate-200); border-bottom: 1px solid var(--slate-200); margin: 80px 0;">
    <div class="max-w-screen">
        <h2 style="font-family: 'Playfair Display', serif; font-size: 32px; color: var(--navy); margin-bottom: 8px;">Legal AI Ethics & Compliance Resources</h2>
        <p style="color: var(--slate-600); margin-bottom: 32px;">Regulatory frameworks and adoption guides for modern law firms.</p>
        <div class="ethics-grid">
            <a href="/blog/pennsylvania-trial-lawyers-ai-ethics-legal-intake.html" class="ethics-card">
                <h4>Pennsylvania AI Ethics Guide</h4>
                <p>A practical framework for PA trial lawyers adopting AI in legal intake and merit review.</p>
            </a>
            <a href="/blog/illinois-trial-lawyers-ai-ethics-legal-intake.html" class="ethics-card">
                <h4>Illinois AI Ethics Guide</h4>
                <p>Ethics and Section 2-622 compliance for Illinois firm AI adoption and automated screening.</p>
            </a>
            <a href="/blog/new-york-trial-lawyers-ai-ethics-legal-intake.html" class="ethics-card">
                <h4>New York AI Ethics Guide</h4>
                <p>Navigating 22 NYCRR Part 1200 and AI in New York Medical Malpractice intake.</p>
            </a>
        </div>
    </div>
</section>
"""

def clean_city_name(filename):
    name = filename.replace('.html', '').replace('-', ' ').replace('medmal ', '').title()
    if name == 'Nyc': return 'New York City'
    if name == 'La': return 'Los Angeles'
    if name == 'Washington Dc': return 'Washington, D.C.'
    return name

def generate_cities_html():
    medmal_pages = []
    city_pages = []
    
    # Precise crawl
    for root, dirs, files in os.walk(locations_dir):
        for file in files:
            if not file.endswith('.html') or file == 'index.html':
                continue
            
            rel_path = os.path.relpath(os.path.join(root, file), base_dir)
            display_name = clean_city_name(file)
            
            # Categorize
            if 'medmal-' in file:
                medmal_pages.append({'name': display_name, 'path': '/' + rel_path})
            else:
                city_pages.append({'name': display_name, 'path': '/' + rel_path})

    # Deduplicate main city list (prefer non-medmal for the main link)
    seen = {}
    for p in sorted(city_pages, key=lambda x: x['name']):
        if p['name'] not in seen:
            seen[p['name']] = p
    
    medmal_grid = ""
    for p in sorted(medmal_pages, key=lambda x: x['name']):
        medmal_grid += f'            <a href="{p["path"]}" class="city-link" style="border-color: #ef4444; background: #fef2f2; color: #b91c1c;">{p["name"]} (MedMal)</a>\n'
        
    city_grid = ""
    for name in sorted(seen.keys()):
        p = seen[name]
        city_grid += f'            <a href="{p["path"]}" class="city-link">{name}</a>\n'

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>LexiFlow AI | Service Areas - National Legal AI Network</title>
  <meta name="description" content="LexiFlow provides enterprise-grade AI legal intake across 200+ US cities. Explore our local service areas and high-merit MedMal review markets." />
  <link rel="icon" type="image/svg+xml" href="/branding/logo-icon.svg">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <style>{STYLE}</style>
</head>
<body>
  {HEADER}
  <header class="hero">
    <div class="max-w-screen">
      <div style="display: inline-block; padding: 8px 16px; background: rgba(201, 168, 76, 0.1); color: var(--gold); border-radius: 100px; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 24px;">National Service Network</div>
      <h1>Local Intelligence. <span>National Scale.</span></h1>
      <p>LexiFlow's Reasoning AI is transforming intake for law firms across the United States. Select your market to see our impact.</p>
    </div>
  </header>

  <section class="max-w-screen">
    <div style="margin-top: 40px; padding: 48px; background: #fff; border: 1px solid var(--slate-200); border-radius: 32px; box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);">
        <h2 style="font-family: 'Playfair Display', serif; font-size: 28px; margin-bottom: 12px; color: var(--navy);">AI Medical Merit Review Markets</h2>
        <p style="color: var(--slate-600); margin-bottom: 32px;">Specialized MeritScan™ intake for high-stakes Medical Malpractice and Surgical Error litigation.</p>
        <div class="city-grid" style="padding: 0; margin-bottom: 0;">
{medmal_grid}
        </div>
    </div>
    
    <h2 style="font-family: 'Playfair Display', serif; font-size: 32px; margin-top: 80px; margin-bottom: 12px; color: var(--navy);">National Personal Injury Network</h2>
    <p style="color: var(--slate-600); margin-bottom: 40px;">Localized AI intake solutions for personal injury firms in every major jurisdiction.</p>
    <div class="city-grid">
{city_grid}
    </div>
  </section>

  {ETHICS_SECTION}

  <section class="max-w-screen" style="text-align: center; padding: 40px 0;">
    <h2 style="font-family: 'Playfair Display', serif; font-size: 32px; color: var(--navy); margin-bottom: 24px;">Don't see your city?</h2>
    <p style="color: var(--slate-600); max-width: 600px; margin: 0 auto 32px;">LexiFlow can be deployed for any firm, anywhere in the United States. We support custom jurisdiction tuning for all 50 states.</p>
    <a href="/pricing.html" class="btn-cta" style="display: inline-block;">Start 24/7 AI Intake</a>
  </section>

  {FOOTER}
  <script>
    document.querySelector('.nav-toggle').addEventListener('click', function() {{
      document.getElementById('navLinks').classList.toggle('active');
    }});
  </script>
</body>
</html>"""
    with open(os.path.join(base_dir, 'cities.html'), 'w') as f:
        f.write(content)

def generate_locations_index():
    regions = {
        "Northeast": ["Connecticut", "Massachusetts", "New Jersey", "New York", "Pennsylvania", "Vermont", "Maryland", "District Of Columbia"],
        "Midwest": ["Illinois", "Indiana", "Iowa", "Kansas", "Michigan", "Minnesota", "Missouri", "Nebraska", "North Dakota", "Ohio", "South Dakota", "Wisconsin"],
        "South": ["Alabama", "Arkansas", "Florida", "Georgia", "Kentucky", "Louisiana", "Mississippi", "North Carolina", "Oklahoma", "South Carolina", "Tennessee", "Texas", "Virginia", "West Virginia"],
        "West": ["Alaska", "Arizona", "California", "Colorado", "Hawaii", "Idaho", "Montana", "Nevada", "New Mexico", "Oregon", "Utah", "Washington", "Wyoming"],
        "Territories": ["Puerto Rico"]
    }
    
    region_html = ""
    for region, states in regions.items():
        state_links = ""
        for state in sorted(states):
            state_slug = state.lower().replace(' ', '-')
            state_path = f"/locations/{state_slug}/"
            if os.path.exists(os.path.join(locations_dir, state_slug)):
                state_links += f'        <a href="{state_path}" class="city-link">{state}</a>\n'
        
        if state_links:
            region_html += f"""
    <div style="margin-top: 64px;">
        <h2 style="font-family: 'Playfair Display', serif; font-size: 24px; color: var(--navy); margin-bottom: 12px; display: flex; align-items: center; gap: 12px;">
            <span style="width: 32px; height: 2px; background: var(--gold);"></span> {region}
        </h2>
        <div class="city-grid" style="padding-top: 16px;">
{state_links}
        </div>
    </div>"""

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>National AI Legal Directory | LexiFlow</title>
  <meta name="description" content="Nationwide directory of LexiFlow AI legal intake solutions. Explore state-specific jurisdictional AI tuning for US law firms." />
  <link rel="icon" type="image/svg+xml" href="/branding/logo-icon.svg">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <style>{STYLE}</style>
</head>
<body>
  {HEADER}
  <header class="hero">
    <div class="max-w-screen">
      <div style="display: inline-block; padding: 8px 16px; background: rgba(201, 168, 76, 0.1); color: var(--gold); border-radius: 100px; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 24px;">Nationwide Network</div>
      <h1>Legal AI <span>State Directory</span></h1>
      <p>LexiFlow provides jurisdiction-specific AI intake across all 50 states. Select your state to see local compliance and performance metrics.</p>
    </div>
  </header>

  <section class="max-w-screen">
{region_html}
  </section>

  {ETHICS_SECTION}

  {FOOTER}
  <script>
    document.querySelector('.nav-toggle').addEventListener('click', function() {{
      document.getElementById('navLinks').classList.toggle('active');
    }});
  </script>
</body>
</html>"""
    with open(os.path.join(locations_dir, 'index.html'), 'w') as f:
        f.write(content)

generate_cities_html()
generate_locations_index()
print("Refactored cities.html and locations/index.html to premium, clean standards.")
