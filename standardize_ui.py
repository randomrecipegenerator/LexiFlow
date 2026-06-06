import os
import re

files_to_update = [
    "ai-intake-agent.html",
    "ai-medical-chronologies.html",
    "discovery-vault.html",
    "settlement-predictor.html",
    "depolens-ai.html",
    "compliance-shield.html",
    "roi-calculator.html",
    "pricing.html",
    "dashboard.html",
    "cities.html",
    "index.html",
    "signup.html",
    "demo.html",
    "depolens-app.html",
    "medical-chronologies-app.html"
]

# Normalize path to root
base_path = "/home/team/shared/LexiFlow-Final"

blog_dir = os.path.join(base_path, "blog")
if os.path.exists(blog_dir):
    for filename in os.listdir(blog_dir):
        if filename.endswith(".html"):
            files_to_update.append(os.path.join("blog", filename))

header = """<nav><div class="nav-container">
    <a href="/" class="logo"><span>LF</span> LexiFlow</a>
    <ul class="nav-links" id="navLinks">
      <li><a href="/pricing.html">Pricing</a></li>
      <li><a href="/dashboard.html">Dashboard</a></li>
      <li><a href="/blog/index.html">Blog</a></li>
      <li><a href="/roi-calculator.html">ROI Calculator</a></li>
      <li><a href="/cities.html">Areas We Serve</a></li>
      <li><a href="/signup.html" class="btn-cta">Get Started</a></li>
    </ul>
    <button class="nav-toggle">☰</button>
  </div></nav>"""

footer = """  <footer class="footer">
    <div class="footer-container">
      <div class="footer-col">
        <a href="/" class="footer-logo"><span>LF</span> LexiFlow</a>
        <p style="color: var(--slate-400); font-size: 14px;">The orchestration layer for high-stakes litigation. Reasoning AI for high-growth firms.</p>
      </div>
      <div class="footer-col">
        <h4>Products</h4>
        <ul>
          <li><a href="/ai-intake-agent.html">LexiFlow Intake</a></li>
          <li><a href="/ai-medical-chronologies.html">Medical Review</a></li>
          <li><a href="/discovery-vault.html">Discovery-Vault™</a></li>
          <li><a href="/settlement-predictor.html">Settlement-Predictor Pro™</a></li>
          <li><a href="/depolens-ai.html">DepoLens™ AI</a></li>
          <li><a href="/compliance-shield.html">Compliance-Shield™</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Top Markets</h4>
        <ul>
          <li><a href="/locations/california/medmal-la.html">Los Angeles (MedMal)</a></li>
          <li><a href="/locations/california/medmal-san-francisco.html">San Francisco (MedMal)</a></li>
          <li><a href="/locations/new-york/medmal-nyc.html">New York City (MedMal)</a></li>
          <li><a href="/locations/illinois/medmal-chicago.html">Chicago (MedMal)</a></li>
          <li><a href="/cities.html">View All Cities</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Legal</h4>
        <ul>
          <li><a href="/privacy.html">Privacy Policy</a></li>
          <li><a href="/terms.html">Terms of Service</a></li>
          <li><a href="/soc2.html">SOC2 Compliance</a></li>
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
      &copy; 2026 LexiFlow Technologies Inc. All rights reserved.
    </div>
  </footer>
<script src="/shared-layout.js"></script>"""

for filename in files_to_update:
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename} (not found)")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace Nav
    new_content = re.sub(r'<nav.*?>.*?</nav>', header, content, flags=re.DOTALL)
    if new_content == content and filename.startswith("blog"):
        # For blog pages that use <header> instead of <nav>
        new_content = header + "\n" + content
    
    # Replace Footer
    new_content = re.sub(r'<footer.*?>.*?</footer>\s*(<script src="/shared-layout.js"></script>)?', footer, new_content, flags=re.DOTALL)
    
    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Updated {filename}")
