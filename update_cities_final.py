import os
import glob

base_dir = '/home/team/shared/LexiFlow-Final'
locations_dir = os.path.join(base_dir, 'locations')
cities_file = os.path.join(base_dir, 'cities.html')

# 1. Collect all cities
city_pages = []
for html_path in glob.glob(os.path.join(locations_dir, '**', '*.html'), recursive=True):
    if 'index.html' in html_path:
        continue
    
    # Get relative path from base_dir
    rel_path = os.path.relpath(html_path, base_dir)
    # Get filename without extension and format for display
    filename = os.path.basename(html_path)
    city_name = filename.replace('.html', '').replace('-', ' ').replace('medmal ', 'Medical Malpractice ').title()
    
    city_pages.append({'name': city_name, 'path': '/' + rel_path})

# Sort alphabetically by name
city_pages.sort(key=lambda x: x['name'])

# 2. Generate the grid HTML
grid_html = ""
for city in city_pages:
    grid_html += f'            <a href="{city["path"]}" class="city-link">{city["name"]}</a>\n'

# 3. Create the final HTML
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="google-site-verification" content="SdZcqCNhIJHLlfx2BU22unsBd6smFsTf7o6pv-np5Zk" />
  <title>LexiFlow AI | Service Areas - Local AI Legal Intake</title>
  <meta name="description" content="LexiFlow provides enterprise-grade AI legal intake across the United States. Explore our local service areas and see how we help firms in your city." />
  <link rel="icon" type="image/svg+xml" href="/branding/logo-icon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <style>
    :root {{
      --navy: #0f172a; --gold: #c9a84c; --gold-light: #e2c96e;
      --slate-50: #f8fafc; --slate-100: #f1f5f9; --slate-200: #e2e8f0; --slate-400: #94a3b8; --slate-600: #475569;
      --slate-900: #0f172a; --max-width: 1200px;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Inter', sans-serif; background: #fff; color: var(--slate-900); line-height: 1.6; padding-top: 80px; }}
    
    nav {{ position: fixed; top: 0; width: 100%; height: 80px; background: rgba(255,255,255,0.98); border-bottom: 1px solid var(--slate-200); z-index: 1000; display: flex; align-items: center; }}
    .nav-container {{ max-width: var(--max-width); margin: 0 auto; width: 100%; padding: 0 40px; display: flex; justify-content: space-between; align-items: center; }}
    .logo {{ font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: var(--navy); text-decoration: none; display: flex; align-items: center; gap: 12px; }}
    .logo span {{ background: var(--navy); color: var(--gold); padding: 4px 8px; border-radius: 4px; font-size: 18px; }}
    .nav-links {{ display: flex; gap: 32px; list-style: none; }}
    .nav-links a {{ text-decoration: none; color: var(--slate-600); font-weight: 500; font-size: 15px; }}
    .nav-links a:hover {{ color: var(--navy); }}
    .btn-cta {{ background: var(--gold); color: var(--navy); padding: 12px 24px; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 14px; }}
    .nav-toggle {{ display: none; background: none; border: none; font-size: 24px; cursor: pointer; color: var(--navy); }}

    .hero {{ padding: 100px 0 60px; background: radial-gradient(40% 40% at 50% 0%, rgba(37, 99, 235, 0.03) 0%, transparent 100%); text-align: center; }}
    .max-w-screen {{ max-width: var(--max-width); margin: 0 auto; padding: 0 40px; }}
    .hero h1 {{ font-family: 'Playfair Display', serif; font-size: 56px; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 24px; line-height: 1.1; color: var(--navy); }}
    .hero p {{ font-size: 20px; color: var(--slate-600); max-width: 700px; margin: 0 auto; line-height: 1.6; }}

    .city-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; padding: 64px 0; }}
    .city-link {{ display: block; padding: 20px; background: var(--slate-50); border: 1px solid var(--slate-200); border-radius: 12px; font-weight: 600; text-decoration: none; color: var(--navy); transition: all 0.2s ease; text-align: center; font-size: 15px; }}
    .city-link:hover {{ border-color: var(--gold); background: white; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); transform: translateY(-3px); color: var(--gold); }}

    .cta-section {{ background: var(--navy); color: white; border-radius: 32px; padding: 80px; text-align: center; margin: 40px 0 80px; }}
    .cta-section h2 {{ font-family: 'Playfair Display', serif; font-size: 40px; font-weight: 800; margin-bottom: 24px; letter-spacing: -0.02em; }}
    .cta-section p {{ font-size: 18px; color: var(--slate-400); margin-bottom: 40px; }}
    .btn-primary {{ background: var(--gold); color: var(--navy); padding: 16px 32px; border-radius: 8px; font-weight: 600; font-size: 16px; text-decoration: none; display: inline-block; transition: all 0.2s; }}
    .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}

    footer {{ background: var(--navy); color: var(--slate-400); padding: 80px 0 40px; border-top: 1px solid rgba(255,255,255,0.1); }}
    .footer-container {{ max-width: var(--max-width); margin: 0 auto; padding: 0 40px; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; }}
    .footer-logo {{ font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: #fff; text-decoration: none; margin-bottom: 20px; display: block; }}
    .footer-col h4 {{ color: #fff; margin-bottom: 20px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em; }}
    .footer-col ul {{ list-style: none; }}
    .footer-col ul li {{ margin-bottom: 12px; }}
    .footer-col ul a {{ color: var(--slate-400); text-decoration: none; font-size: 14px; }}
    .footer-col ul a:hover {{ color: var(--gold); }}
    .footer-bottom {{ max-width: var(--max-width); margin: 60px auto 0; padding: 40px 40px 0; border-top: 1px solid rgba(255,255,255,0.1); font-size: 13px; text-align: center; }}

    @media (max-width: 768px) {{
      .nav-container {{ padding: 0 20px; }}
      .nav-links {{ display: none; position: absolute; top: 80px; left: 0; width: 100%; background: #fff; flex-direction: column; padding: 20px; gap: 20px; border-bottom: 1px solid var(--slate-200); box-shadow: 0 10px 15px rgba(0,0,0,0.05); }}
      .nav-links.active {{ display: flex; }}
      .nav-toggle {{ display: block; }}
      .btn-cta {{ display: none; }}
      .hero h1 {{ font-size: 36px; }}
      .footer-container {{ grid-template-columns: 1fr; gap: 40px; text-align: center; }}
      .city-grid {{ grid-template-columns: 1fr; }}
      .cta-section {{ padding: 40px 20px; border-radius: 0; }}
    }}
  </style>
</head>
<body>
  <nav><div class="nav-container">
    <a href="/" class="logo"><span>LF</span> LexiFlow</a>
    <ul class="nav-links" id="navLinks">
      <li><a href="/dashboard.html">Dashboard</a></li>
      <li><a href="/pricing.html">Pricing</a></li>
      <li><a href="/blog.html">Blog</a></li>
      <li><a href="/cities.html">Areas We Serve</a></li>
      <li><a href="/pricing.html" class="btn-cta">Get Started</a></li>
    </ul>
    <button class="nav-toggle" onclick="document.getElementById('navLinks').classList.toggle('active')">☰</button>
  </div></nav>

  <header class="hero">
    <div class="max-w-screen">
      <div style="display: inline-block; padding: 8px 16px; background: rgba(201, 168, 76, 0.1); color: var(--gold); border-radius: 100px; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 24px;">National Service Network</div>
      <h1>Local Reach. <span>National Scale.</span></h1>
      <p>LexiFlow's Reasoning AI is transforming intake for law firms across the United States. Select your market to see how we drive conversion.</p>
    </div>
  </header>

  <section class="max-w-screen">
    <div class="city-grid">
{grid_html}
    </div>

    <div class="cta-section">
      <h2>Don't see your city?</h2>
      <p>LexiFlow can be deployed for any firm, anywhere in the United States. Schedule a custom market analysis today.</p>
      <a href="/roi-calculator.html" class="btn-primary">Get Started Now</a>
    </div>
  </section>

  <footer>
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
  </footer>

  <script>
    // Simple toggle for mobile nav
    document.querySelector('.nav-toggle').addEventListener('click', function() {{
      document.getElementById('navLinks').classList.toggle('active');
    }});
  </script>
</body>
</html>
"""

with open(cities_file, 'w') as f:
    f.write(html_content)

print(f"Successfully generated cities.html with {len(city_pages)} cities.")
