import os
import re

# Standard NAV_BAR and FOOTER with absolute paths
NAV_BAR = """
<nav style="position: fixed; top: 0; width: 100%; height: 80px; background: rgba(255,255,255,0.98); border-bottom: 1px solid #e2e8f0; z-index: 1000; display: flex; align-items: center; font-family: 'Inter', sans-serif;">
  <div style="max-width: 1200px; margin: 0 auto; width: 100%; padding: 0 40px; display: flex; justify-content: space-between; align-items: center;">
    <a href="/index.html" style="font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: #0f172a; text-decoration: none; display: flex; align-items: center; gap: 12px;">
      <span style="background: #0f172a; color: #c9a84c; padding: 4px 8px; border-radius: 4px; font-size: 18px;">LF</span> LexiFlow
    </a>
    <ul style="display: flex; gap: 32px; list-style: none; margin: 0; padding: 0;">
      <li><a href="/dashboard.html" style="text-decoration: none; color: #475569; font-weight: 500; font-size: 15px;">Attorney Portal</a></li>
      <li><a href="/pricing.html" style="text-decoration: none; color: #475569; font-weight: 500; font-size: 15px;">Capabilities</a></li>
      <li><a href="/blog.html" style="text-decoration: none; color: #475569; font-weight: 500; font-size: 15px;">Insights</a></li>
      <li><a href="/cities.html" style="text-decoration: none; color: #475569; font-weight: 500; font-size: 15px;">Areas We Serve</a></li>
    </ul>
    <a href="/pricing.html" style="background: #c9a84c; color: #0f172a; padding: 12px 24px; border-radius: 6px; font-weight: 600; text-decoration: none; font-size: 14px;">Request Access</a>
  </div>
</nav>
<div style="height: 80px;"></div>
"""

FOOTER = """
<footer style="background: #0f172a; color: #94a3b8; padding: 80px 0 40px; font-family: 'Inter', sans-serif;">
  <div style="max-width: 1200px; margin: 0 auto; padding: 0 40px; display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 80px;">
    <div>
      <a href="/index.html" style="font-family: 'Playfair Display', serif; font-weight: 700; font-size: 24px; color: #fff; text-decoration: none; margin-bottom: 20px; display: block;">LexiFlow</a>
      <p style="font-size: 14px; line-height: 1.6;">Enterprise Legal Intelligence. Empowering the next generation of top-tier law firms.</p>
    </div>
    <div>
      <h4 style="color: #fff; margin-bottom: 20px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em;">Platform</h4>
      <ul style="list-style: none; padding: 0;">
        <li style="margin-bottom: 12px;"><a href="/pricing.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Pricing</a></li>
        <li style="margin-bottom: 12px;"><a href="/dashboard.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Attorney Portal</a></li>
        <li style="margin-bottom: 12px;"><a href="/blog.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Legal Insights</a></li>
        <li style="margin-bottom: 12px;"><a href="/cities.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Areas We Serve</a></li>
      </ul>
    </div>
    <div>
      <h4 style="color: #fff; margin-bottom: 20px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.1em;">Support</h4>
      <ul style="list-style: none; padding: 0;">
        <li style="margin-bottom: 12px;"><a href="#" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Privacy Policy</a></li>
        <li style="margin-bottom: 12px;"><a href="/terms.html" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Terms of Service</a></li>
        <li style="margin-bottom: 12px;"><a href="mailto:leads@lexiflow.co" style="color: #94a3b8; text-decoration: none; font-size: 14px;">Contact Relations</a></li>
      </ul>
    </div>
  </div>
  <div style="max-width: 1200px; margin: 60px auto 0; padding: 40px 40px 0; border-top: 1px solid rgba(255,255,255,0.1); font-size: 13px; text-align: center;">
    &copy; 2026 LexiFlow Legal Suite. All Rights Reserved.
  </div>
</footer>
"""

# Re-inject hardened styles but keep content
STYLING = """
<style>
  :root { --navy: #0f172a; --gold: #c9a84c; --slate-50: #f8fafc; --slate-200: #e2e8f0; --slate-400: #94a3b8; --slate-600: #475569; }
  body { font-family: 'Inter', sans-serif; background: #fff; color: var(--navy); line-height: 1.6; margin: 0; }
  .container { max-width: 1200px; margin: 0 auto; padding: 0 40px; }
  .hero { background: var(--navy); color: #fff; padding: 100px 0; text-align: center; }
  .hero h1 { font-family: 'Playfair Display', serif; font-size: 48px; margin-bottom: 16px; }
  .hero h1 span.highlight { color: var(--gold); font-style: italic; }
  .hero p.subtitle { font-size: 18px; color: var(--slate-400); max-width: 700px; margin: 0 auto 40px; }
  .hero-badges { display: flex; gap: 12px; justify-content: center; margin-bottom: 24px; }
  .hero-badge { background: rgba(255,255,255,0.1); color: #fff; padding: 4px 12px; border-radius: 100px; font-size: 12px; font-weight: 600; }
  .btn { display: inline-block; padding: 14px 28px; border-radius: 6px; text-decoration: none; font-weight: 600; transition: all 0.2s; }
  .btn-primary { background: var(--gold); color: var(--navy); }
  .btn-secondary { border: 1px solid var(--slate-400); color: #fff; margin-left: 12px; }
  .section { padding: 80px 0; }
  .section-header { text-align: center; margin-bottom: 48px; }
  .section-label { color: var(--gold); text-transform: uppercase; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; display: block; margin-bottom: 8px; }
  .section h2 { font-family: 'Playfair Display', serif; font-size: 32px; color: var(--navy); }
  .features-grid-2 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 32px; }
  .feature-card { background: #fff; padding: 32px; border-radius: 12px; border: 1px solid var(--slate-200); }
  .feature-icon { font-size: 24px; margin-bottom: 16px; }
  .feature-card h3 { font-family: 'Playfair Display', serif; font-size: 20px; margin-bottom: 12px; }
  .feature-card p { color: var(--slate-600); font-size: 15px; }
  .stats-bar { background: var(--navy); color: #fff; padding: 40px 0; display: flex; justify-content: space-around; text-align: center; }
  .stat h4 { color: var(--gold); font-size: 32px; margin: 0; }
  .stat p { font-size: 14px; color: var(--slate-400); margin: 0; }
  .lead-magnet { background: var(--slate-50); padding: 48px; border-radius: 12px; text-align: center; border: 1px solid var(--slate-200); }
  .magnet-btn { display: inline-block; background: var(--navy); color: #fff; padding: 14px 28px; border-radius: 6px; text-decoration: none; font-weight: 600; margin-top: 16px; }
  .cta-section { background: var(--gold); padding: 80px 0; text-align: center; }
  .cta-section h2 { font-family: 'Playfair Display', serif; font-size: 36px; margin-bottom: 16px; }
  .cta-actions { margin-top: 24px; }
  @media (max-width: 768px) { .features-grid-2 { grid-template-columns: 1fr; } .stats-bar { flex-direction: column; gap: 24px; } }
</style>
"""

FILES = [
    "ai-intake-agent.html", "voice-ai-receptionist.html", 
    "ai-medical-chronologies.html", "auto-document-drafter.html", 
    "depolens-ai.html", "settlement-estimator.html"
]

repo_dir = "/home/agent-lead/lexiflow-repo"

for filename in FILES:
    filepath = os.path.join(repo_dir, filename)
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 1. Clean existing Nav, Footer, and Style tags
    content = re.sub(r'<nav.*?>.*?</nav>', '', content, flags=re.DOTALL)
    content = re.sub(r'<footer.*?>.*?</footer>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<link rel="stylesheet".*?>', '', content)
    content = re.sub(r'<div id="navbar".*?>.*?</div>', '', content, flags=re.DOTALL) # Some use this
    content = re.sub(r'<div class="height: 80px;"></div>', '', content)

    # 2. Re-inject Hardened Nav & Footer, and absolute path the body links
    if "<body>" in content:
        content = content.replace("<body>", "<body>" + NAV_BAR)
    if "</body>" in content:
        content = content.replace("</body>", FOOTER + "</body>")
    
    # Absolute paths for known pages
    pages = ["index.html", "pricing.html", "blog.html", "cities.html", "dashboard.html"]
    for p in pages:
        content = content.replace(f'href="{p}"', f'href="/{p}"')
        content = content.replace(f'href="../{p}"', f'href="/{p}"')

    # 3. Inject Styling into Head
    if "</head>" in content:
        content = content.replace("</head>", STYLING + "</head>")

    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Repaired and Hardened {filename}")
