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
    "medical-chronologies-app.html",
    "ai-legal-intake-software.html",
    "medical-chronology-software.html",
    "personal-injury-software.html"
]

# Normalize path to root
base_path = "/home/team/shared/LexiFlow-Final"

blog_dir = os.path.join(base_path, "blog")
if os.path.exists(blog_dir):
    for filename in os.listdir(blog_dir):
        if filename.endswith(".html"):
            files_to_update.append(os.path.join("blog", filename))

resources_dir = os.path.join(base_path, "resources")
if os.path.exists(resources_dir):
    for filename in os.listdir(resources_dir):
        if filename.endswith(".html"):
            files_to_update.append(os.path.join("resources", filename))

hardened_dir = os.path.join(base_path, "hardened-suite")
if os.path.exists(hardened_dir):
    for filename in os.listdir(hardened_dir):
        if filename.endswith(".html"):
            files_to_update.append(os.path.join("hardened-suite", filename))
    
    hardened_resources_dir = os.path.join(hardened_dir, "resources")
    if os.path.exists(hardened_resources_dir):
        for filename in os.listdir(hardened_resources_dir):
            if filename.endswith(".html"):
                files_to_update.append(os.path.join("hardened-suite", "resources", filename))

header = """<nav><div class="nav-container">
    <a href="/" class="logo"><span>LF</span> LexiFlow</a>
    <ul class="nav-links" id="navLinks">
      <li><a href="/pricing.html">Pricing</a></li>
      <li><a href="/dashboard.html">Dashboard</a></li>
      <li><a href="/blog/index.html">Blog</a></li>
      <li class="resources-dropdown">
        <a href="#">Resources ▾</a>
        <div class="resources-menu">
          <a href="/resources/medical-chronology-template.html">Medical Chronology Template</a>
          <a href="/resources/medical-chronology-sample.html">Medical Chronology Sample</a>
          <a href="/resources/medical-record-review-checklist.html">Record Review Checklist</a>
        </div>
      </li>
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
      &copy; 2026 LexiFlow AI. All rights reserved.
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
    
    # First, remove any existing injected nav if it's at the very top (fix previous run)
    content = content.replace(header + "\n", "")
    content = content.replace(header, "")

    # Replace Nav
    if '<nav' in content:
        new_content = re.sub(r'<nav.*?>.*?</nav>', header, content, flags=re.DOTALL)
    else:
        # If no nav, insert after body
        new_content = re.sub(r'(<body.*?>)', r'\1\n' + header, content, flags=re.DOTALL)
    
    # Replace Footer
    if '<footer' in content:
        new_content = re.sub(r'<footer.*?>.*?</footer>\s*(<script src="/shared-layout.js"></script>)?', footer, new_content, flags=re.DOTALL)
    else:
        # If no footer, insert before </body>
        new_content = re.sub(r'(</body>)', footer + r'\n\1', new_content, flags=re.DOTALL)
    
    # Fix canonicals and links if in blog
    if filename.startswith("blog"):
        # Ensure canonical uses .html
        new_content = re.sub(r'<link rel="canonical" href="https://lexiflow.co/blog/(.*?)">', r'<link rel="canonical" href="https://lexiflow.co/blog/\1.html">', new_content)
        # Ensure email is unified
        new_content = re.sub(r'mailto:.*?@.*?\..*?"', 'mailto:lexiflow-legal-suite-88a6f8e9@ctomail.io"', new_content)

    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"Updated {filename}")
