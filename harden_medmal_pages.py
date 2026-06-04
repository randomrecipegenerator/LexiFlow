import os
import glob
import re

base_dir = '/home/team/shared/LexiFlow-Final'
locations_dir = os.path.join(base_dir, 'locations')

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

STYLE_EXT = """
    /* Mobile-Friendly Adjustments */
    @media (max-width: 768px) {
        .container, .nav-container, .max-w-screen, .max-w, .hero-container, .footer-container { 
            padding-left: 20px !important; 
            padding-right: 20px !important; 
            width: 100% !important;
            max-width: 100% !important;
        }
        .grid, .highlight-grid, .faq-grid, .pricing-grid, .assoc-grid, .city-grid { 
            grid-template-columns: 1fr !important; 
            display: grid !important;
            gap: 20px !important;
        }
        .hero-container, .footer-container, .section-header { 
            grid-template-columns: 1fr !important; 
            text-align: center !important; 
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
        }
        .hero-text, .hero-image, .footer-col {
            width: 100% !important;
            margin-bottom: 30px !important;
        }
        h1 { font-size: 28px !important; line-height: 1.2 !important; }
        h2 { font-size: 24px !important; }
        h3 { font-size: 20px !important; }
        
        /* Nav adjustments */
        nav, .nav { height: auto !important; padding: 10px 0 !important; min-height: 60px; position: fixed; top: 0; width: 100%; background: #fff; z-index: 1000; border-bottom: 1px solid #e2e8f0; }
        .nav-container { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 20px; height: 80px; }
        .nav-links { flex-direction: column !important; align-items: center !important; gap: 10px !important; display: none !important; width: 100% !important; order: 3; padding: 20px 0 !important; position: absolute; top: 80px; left: 0; background: #fff; }
        .nav-links.active { display: flex !important; }
        .nav-toggle { display: block !important; background: none; border: none; font-size: 24px; cursor: pointer; color: #0f172a; }
        .btn-cta, .btn-primary { padding: 8px 16px !important; font-size: 13px !important; }
        
        /* Card and Feature adjustments */
        .card, .pricing-card, .highlight-item, .faq-item, .assoc-card, .city-link { 
            margin-bottom: 20px !important; 
            width: 100% !important;
            min-width: 0 !important;
        }
    }
    
    /* Internal Page Styles */
    :root {
      --navy: #0f172a; --gold: #c9a84c; --gold-light: #e2c96e;
      --slate-50: #f8fafc; --slate-100: #f1f5f9; --slate-200: #e2e8f0; --slate-400: #94a3b8; --slate-600: #475569;
      --slate-900: #0f172a; --max-width: 1200px;
    }
    body { margin: 0; padding-top: 80px; }
    nav { position: fixed; top: 0; width: 100%; height: 80px; background: rgba(255,255,255,0.98); border-bottom: 1px solid var(--slate-200); z-index: 1000; display: flex; align-items: center; }
    .nav-container { max-width: var(--max-width); margin: 0 auto; width: 100%; padding: 0 40px; display: flex; justify-content: space-between; align-items: center; }
    .logo { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: var(--navy); text-decoration: none; display: flex; align-items: center; gap: 12px; }
    .logo span { background: var(--navy); color: var(--gold); padding: 4px 8px; border-radius: 4px; font-size: 18px; }
    .nav-links { display: flex; gap: 32px; list-style: none; }
    .nav-links a { text-decoration: none; color: var(--slate-600); font-weight: 500; font-size: 15px; }
    .nav-links a:hover { color: var(--navy); }
    .btn-cta { background: var(--gold); color: var(--navy); padding: 12px 24px; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 14px; }
    .nav-toggle { display: none; }

    footer { background: var(--navy); color: var(--slate-400); padding: 80px 0 40px; border-top: 1px solid rgba(255,255,255,0.1); }
    .footer-container { max-width: var(--max-width); margin: 0 auto; padding: 0 40px; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; }
    .footer-logo { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: #fff; text-decoration: none; margin-bottom: 20px; display: block; }
    .footer-col h4 { color: #fff; margin-bottom: 20px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em; }
    .footer-col ul { list-style: none; padding: 0; }
    .footer-col ul li { margin-bottom: 12px; }
    .footer-col ul a { color: var(--slate-400); text-decoration: none; font-size: 14px; }
    .footer-col ul a:hover { color: var(--gold); }
    .footer-bottom { max-width: var(--max-width); margin: 60px auto 0; padding: 40px 40px 0; border-top: 1px solid rgba(255,255,255,0.1); font-size: 13px; text-align: center; }
"""

for medmal_file in glob.glob(os.path.join(locations_dir, '**', 'medmal-*.html'), recursive=True):
    with open(medmal_file, 'r') as f:
        content = f.read()
    
    # 1. Clean up potential artifacts
    content = content.replace('href="style.css"', 'href="/style.css"')
    content = content.replace('src="config.js"', 'src="/config.js"')
    content = content.replace('href="branding/', 'href="/branding/')
    content = content.replace('src="branding/', 'src="/branding/')

    # 2. Extract Head and Body
    head_match = re.search(r'<head[^>]*>(.*?)</head>', content, re.DOTALL)
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
    
    if not (head_match and body_match):
        continue
        
    inner_head = head_match.group(1)
    inner_body = body_match.group(1)
    
    # 3. Clean Inner Head (replace style)
    if '<style>' in inner_head:
        inner_head = re.sub(r'<style>.*?</style>', f'<style>{STYLE_EXT}</style>', inner_head, flags=re.DOTALL)
    else:
        inner_head += f'<style>{STYLE_EXT}</style>'
        
    # 4. Clean Inner Body (deep clean)
    # Remove existing structural elements
    inner_body = re.sub(r'<header.*?</header>', '', inner_body, flags=re.DOTALL)
    inner_body = re.sub(r'<footer.*?</footer>', '', inner_body, flags=re.DOTALL)
    inner_body = re.sub(r'<nav.*?</nav>', '', inner_body, flags=re.DOTALL)
    inner_body = re.sub(r'<main.*?>', '', inner_body, flags=re.DOTALL)
    inner_body = re.sub(r'</main>', '', inner_body, flags=re.DOTALL)
    # Remove any extra scripts injected by previous runs
    inner_body = re.sub(r'<script.*?</script>', '', inner_body, flags=re.DOTALL)
    
    # 5. Reassemble Final File
    final_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
{inner_head}
</head>
<body class="bg-slate-50 text-slate-900">
{HEADER}
<main>
{inner_body}
</main>
{FOOTER}
<script src="/config.js"></script>
<script>
    document.querySelector('.nav-toggle').addEventListener('click', function() {{
      document.getElementById('navLinks').classList.toggle('active');
    }});
    function toggleConsultation(label) {{ alert('Demo request initiated: ' + label); }}
</script>
</body>
</html>"""

    with open(medmal_file, 'w') as f:
        f.write(final_content)

print("Standardized and deeply cleaned all Medical Malpractice landing pages.")
