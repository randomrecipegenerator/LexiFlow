import os
import re

# New Standardized Layout Components
NAV_BLOCK = """<nav><div class="nav-container">
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
    <button class="nav-toggle" aria-label="Menu">☰</button>
  </div></nav>"""

FOOTER_BLOCK = """<footer>
    <div class="footer-container">
      <div class="footer-col">
        <a href="/" class="footer-logo">LF LexiFlow</a>
        <p>Advanced Reasoning AI for the Plaintiff-Side Revolution. Automating intake, discovery, and litigation intelligence.</p>
      </div>
      <div class="footer-col">
        <h4>Products</h4>
        <ul>
          <li><a href="/ai-legal-intake-software.html">AI Intake Agent</a></li>
          <li><a href="/voice-ai-receptionist.html">Voice AI Receptionist</a></li>
          <li><a href="/ai-medical-chronologies.html">Medical Chronologies</a></li>
          <li><a href="/auto-document-drafter.html">Auto-Doc Drafter</a></li>
          <li><a href="/discovery-vault.html">Discovery-Vault™</a></li>
          <li><a href="/settlement-predictor.html">Settlement-Predictor Pro™</a></li>
          <li><a href="/depolens-ai.html">DepoLens™ AI</a></li>
          <li><a href="/compliance-shield.html">Compliance-Shield™</a></li>
          <li><a href="/dashboard.html">Analytics Dashboard</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Top Markets</h4>
        <ul>
          <li><a href="/locations/california/los-angeles.html">Los Angeles (MedMal)</a></li>
          <li><a href="/locations/california/san-francisco.html">San Francisco (MedMal)</a></li>
          <li><a href="/locations/new-york/nyc.html">New York City (MedMal)</a></li>
          <li><a href="/locations/illinois/chicago.html">Chicago (MedMal)</a></li>
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
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 LexiFlow Technologies Inc. All rights reserved. | Enterprise-Grade AI for Law Firms.</p>
    </div>
  </footer>"""

BASE_DIR = "/home/team/shared/LexiFlow-Final"

def standardize_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Determine relative path correctly
    rel_dir = os.path.relpath(os.path.dirname(filepath), BASE_DIR)
    if rel_dir == ".":
        rel_path = "./"
    else:
        depth = len(rel_dir.split(os.sep))
        rel_path = "../" * depth
    
    css_link = f'<link rel="stylesheet" href="{rel_path}shared-layout.css">'
    js_script = f'<script src="{rel_path}shared-layout.js"></script>'

    # 1. CSS Link
    if 'shared-layout.css' not in content:
        content = content.replace('</head>', f'{css_link}\n</head>')
    else:
        content = re.sub(r'<link rel="stylesheet" href=".*?shared-layout\.css">', css_link, content)

    # 2. Replace Nav
    # Match any nav/div that is the header navigation
    content = re.sub(r'<body>.*?<nav>.*?</nav>', '<body>' + NAV_BLOCK, content, flags=re.DOTALL)
    # Also handle files that used <div class="nav">
    content = re.sub(r'<body>.*?<div class="nav">.*?</div>\s*</div>\s*</div>', '<body>' + NAV_BLOCK, content, flags=re.DOTALL)
    content = re.sub(r'<body>.*?<div class="nav">.*?</div>', '<body>' + NAV_BLOCK, content, flags=re.DOTALL)

    # 3. Replace Footer
    # Look for footer and standard script tag
    content = re.sub(r'<footer.*?>.*?</footer>\s*(<script src=".*?shared-layout\.js"></script>)?', FOOTER_BLOCK + '\n' + js_script, content, flags=re.DOTALL)

    # 4. Remove old mobile scripts
    content = re.sub(r'<script>\s*\(function\(\) \{\s*var toggle = document\.querySelector\(\'\.nav-toggle\'\);.*?\}\)\(\);\s*</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<script>\s*document\.querySelector\(\'\.nav-toggle\'\)\.addEventListener\(.*?\);\s*</script>', '', content, flags=re.DOTALL)

    # 5. Ensure JS Script is at the very end if not already there
    if 'shared-layout.js' not in content:
        content = content.replace('</body>', f'{js_script}\n</body>')

    # 6. Cleanup local styles
    if '.nav' in content or '.nav-links' in content:
        content = re.sub(r'\.nav\s*\{[^}]*\}', '/* Removed */', content)
        content = re.sub(r'\.nav-links\s*\{[^}]*\}', '/* Removed */', content)
        content = re.sub(r'\.nav-toggle\s*\{[^}]*\}', '/* Removed */', content)
        content = re.sub(r'@media\s*\(max-width:\s*768px\)\s*\{[^}]*\.nav-links[^}]*\}', '/* Removed */', content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def process_dir(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                standardize_file(os.path.join(root, file))

if __name__ == "__main__":
    process_dir(BASE_DIR)
    print("Standardization complete.")
