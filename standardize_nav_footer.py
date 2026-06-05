import os
import re

ROOT_DIR = "/home/team/shared/LexiFlow-Final"

NAV_TEMPLATE = """      <nav><div class="nav-container">
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

FOOTER_TEMPLATE = """      <footer>
    <div class="footer-container">
      <div class="footer-col">
        <a href="/" class="footer-logo">LexiFlow</a>
        <p>Enterprise-grade AI for legal intake and lead qualification. Built for the modern attorney.</p>
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
  </footer>"""

SCRIPT_TEMPLATE = """  <script>
    (function() {
        var toggle = document.querySelector('.nav-toggle');
        var navLinks = document.getElementById('navLinks');
        if (toggle && navLinks) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                navLinks.classList.toggle('active');
            });
        }
    })();
  </script>"""

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace Nav
    if '<nav>' in content:
        content = re.sub(r'<nav>.*?</nav>', NAV_TEMPLATE, content, flags=re.DOTALL)
    else:
        # Insert nav after <body>
        content = re.sub(r'(<body[^>]*>)', r'\1\n' + NAV_TEMPLATE, content, flags=re.IGNORECASE)

    # Replace Footer
    if '<footer>' in content:
        content = re.sub(r'<footer>.*?</footer>', FOOTER_TEMPLATE, content, flags=re.DOTALL)
    else:
        # Insert footer before </body> or at the end
        if '</body>' in content:
            content = re.sub(r'(</body>)', FOOTER_TEMPLATE + r'\n\1', content, flags=re.IGNORECASE)
        else:
            content += "\n" + FOOTER_TEMPLATE

    # Ensure the script is present
    if 'nav-toggle' in content and 'navLinks' in content and '<script>' not in content.split('<footer>')[-1]:
         if '</body>' in content:
            content = re.sub(r'(</body>)', SCRIPT_TEMPLATE + r'\n\1', content, flags=re.IGNORECASE)
         else:
            content += "\n" + SCRIPT_TEMPLATE

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Standardized {filepath}")

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".html"):
                if "ROI_Report_" in file or "template" in file.lower() and "index" not in file.lower():
                    continue
                if ".git" in root or "node_modules" in root:
                    continue
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
