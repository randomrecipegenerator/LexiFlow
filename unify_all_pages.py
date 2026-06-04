import os
import re

# Directory containing the website files
ROOT_DIR = '/home/team/shared/LexiFlow-Final'

# Standard Navigation (Hardened Suite)
NAV = """
  <nav><div class="nav-container">
    <a href="/" class="logo"><span>LF</span> LexiFlow</a>
    <ul class="nav-links" id="navLinks">
      <li><a href="/pricing.html">Pricing</a></li>
      <li><a href="/blog/index.html">Blog</a></li>
      <li><a href="/roi-calculator.html">ROI Calculator</a></li>
      <li><a href="/cities.html">Areas We Serve</a></li>
      <li><a href="/pricing.html" class="btn-cta">Get Started</a></li>
    </ul>
    <button class="nav-toggle">☰</button>
  </div></nav>
"""

# Standard Footer (Hardened Suite)
FOOTER = """
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
"""

# Standard Nav Toggle Script
NAV_SCRIPT = """
    <script>
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
    </script>
"""

def unify_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace Navigation
    new_content = re.sub(r'<nav.*?>.*?</nav>', NAV, content, flags=re.DOTALL)
    
    # 2. Replace Footer
    new_content = re.sub(r'<footer.*?>.*?</footer>', FOOTER, new_content, flags=re.DOTALL)

    # 3. Ensure Nav Script exists and is clean
    if 'var toggle = document.querySelector(\'.nav-toggle\');' in new_content:
        # Replace existing script block to ensure it matches the standard
        new_content = re.sub(r'<script>\s*\(function\(\)\s*{\s*var toggle = document\.querySelector\(\'.nav-toggle\'\);.*?}\)\(\);\s*</script>', NAV_SCRIPT, new_content, flags=re.DOTALL)
    else:
        # Append before </body>
        new_content = new_content.replace('</body>', NAV_SCRIPT + '\n</body>')

    # 4. Global Link Fixes
    new_content = new_content.replace('href="/blog.html"', 'href="/blog/index.html"')
    new_content = new_content.replace('href="/blog"', 'href="/blog/index.html"')
    new_content = new_content.replace('href="/security.html"', 'href="/soc2.html"') # Preferred link
    
    # 5. Fix absolute paths for assets
    new_content = new_content.replace('href="style.css"', 'href="/style.css"')
    new_content = new_content.replace('src="script.js"', 'src="/script.js"')

    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    count = 0
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith('.html'):
                if unify_file(os.path.join(root, file)):
                    count += 1
    print(f"Successfully unified {count} pages.")

if __name__ == "__main__":
    main()
