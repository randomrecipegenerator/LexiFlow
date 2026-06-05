import os

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

# Hardened CSS for section layout
HARDENED_CSS = """
<style>
  :root { --navy: #0f172a; --gold: #c9a84c; --slate-50: #f8fafc; --slate-200: #e2e8f0; --slate-400: #94a3b8; --slate-600: #475569; }
  * { box-sizing: border-box; }
  body { font-family: 'Inter', sans-serif; margin: 0; color: var(--navy); line-height: 1.6; }
  .container { max-width: 1200px; margin: 0 auto; padding: 0 40px; }
  header.hardened-header { padding: 120px 0 60px; background: var(--navy); color: #fff; text-align: center; }
  header.hardened-header h1 { font-family: 'Playfair Display', serif; font-size: 48px; margin-bottom: 16px; }
  header.hardened-header h1 span { color: var(--gold); font-style: italic; }
  header.hardened-header p { font-size: 18px; color: var(--slate-400); max-width: 700px; margin: 0 auto; }
  section.hardened-section { padding: 80px 0; }
  section.hardened-section.alt { background: var(--slate-50); }
  .feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; margin-top: 48px; }
  .feature-card { background: #fff; padding: 32px; border-radius: 12px; border: 1px solid var(--slate-200); }
  .feature-card h3 { font-family: 'Playfair Display', serif; font-size: 20px; margin-bottom: 12px; }
  .feature-card p { color: var(--slate-600); font-size: 15px; }
  .cta-block { background: var(--gold); color: var(--navy); padding: 48px; border-radius: 12px; text-align: center; margin: 48px 0; }
  .cta-block h2 { font-family: 'Playfair Display', serif; font-size: 32px; margin-bottom: 16px; }
  .btn-gold { display: inline-block; background: var(--navy); color: #fff; padding: 16px 32px; border-radius: 6px; text-decoration: none; font-weight: 600; margin-top: 16px; }
  @media (max-width: 768px) { .feature-grid { grid-template-columns: 1fr; } }
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
    
    # 1. Strip all existing <style> and <link rel="stylesheet"> tags to clean the mess
    import re
    content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
    content = re.sub(r'<link rel="stylesheet".*?>', '', content)
    
    # 2. Extract Title and Header Content (Very rough, but looking for <h1> and 1st <p>)
    title_match = re.search(r'<h1>(.*?)</h1>', content, re.DOTALL)
    p_match = re.search(r'<p class="subtitle">(.*?)</p>', content, re.DOTALL)
    if not p_match:
        p_match = re.search(r'</h1>.*?<p>(.*?)</p>', content, re.DOTALL)
    
    h1_text = title_match.group(1) if title_match else "LexiFlow Capability"
    p_text = p_match.group(1) if p_match else "Enterprise-grade legal AI orchestration."

    # 3. Reconstruct the page using the template
    new_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{h1_text.strip()} | LexiFlow Legal Suite</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
  {HARDENED_CSS}
</head>
<body>
  {NAV_BAR}
  
  <header class="hardened-header">
    <div class="container">
      <h1>{h1_text.strip()}</h1>
      <p>{p_text.strip()}</p>
    </div>
  </header>

  <section class="hardened-section">
    <div class="container">
      <div class="cta-block">
        <h2>Enterprise Legal Intelligence</h2>
        <p>Deploy high-stakes AI built for the next generation of top-tier law firms.</p>
        <a href="/pricing.html" class="btn-gold">Request Firm Access</a>
      </div>
    </div>
  </section>

  {FOOTER}
</body>
</html>"""
    
    with open(filepath, 'w') as f:
        f.write(new_html)
    print(f"Fixed and Hardened {filename}")
