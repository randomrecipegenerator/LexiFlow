import os
import re

# Standardized Nav
NAV_HTML = """  <nav><div class="nav-container">
    <a href="/" class="logo"><span>LF</span> LexiFlow</a>
    <ul class="nav-links" id="navLinks">
      <li><a href="/pricing.html">Pricing</a></li>
      <li><a href="/blog/index.html">Blog</a></li>
      <li><a href="/roi-calculator.html">ROI Calculator</a></li>
      <li><a href="/cities.html">Areas We Serve</a></li>
      <li><a href="/signup.html" class="btn-cta">Get Started</a></li>
    </ul>
    <button class="nav-toggle">☰</button>
  </div></nav>"""

# Standardized Footer
FOOTER_HTML = """  <footer>
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
  </footer>"""

# Standardized Mobile Script
SCRIPT_HTML = """  <script>
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

def harden_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove existing nav (look for <nav>...</nav>)
    content = re.sub(r'<nav>.*?</nav>', '', content, flags=re.DOTALL)
    
    # 2. Remove existing footer (look for <footer>...</footer>)
    content = re.sub(r'<footer>.*?</footer>', '', content, flags=re.DOTALL)

    # 3. Remove legacy mobile menu scripts
    content = re.sub(r'<script>\s*\(function\(\)\s*{\s*var toggle = document\.querySelector\(\'\.nav-toggle\'\).*?<\/script>', '', content, flags=re.DOTALL)

    # 4. Inject Nav after <body> tag
    content = re.sub(r'(<body[^>]*>)', r'\1\n' + NAV_HTML, content)

    # 5. Inject Footer and Script before </body> tag
    content = re.sub(r'(</body>)', FOOTER_HTML + '\n' + SCRIPT_HTML + '\n' + r'\1', content)

    # Cleanup any accidental double injections or spacing issues
    content = content.replace('\n\n\n', '\n\n')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                # Skip dashboard and app files that have custom UI
                if file in ['dashboard.html', 'app.html', 'meritscan-app.html', 'depolens-app.html', 'form_view.html']:
                    continue
                filepath = os.path.join(root, file)
                try:
                    harden_file(filepath)
                    print(f"Hardened: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    process_directory("/home/team/shared/LexiFlow-Final")
