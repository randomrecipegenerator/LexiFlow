#!/usr/bin/env python3
"""Replace all footers in LexiFlow HTML files with the standard footer."""
import os, re

ROOT = "/home/team/shared/LexiFlow-Final"

STANDARD_FOOTER = '''  <footer>
    <div class="footer-container">
      <div class="footer-col">
        <a href="/" class="footer-logo">LF LexiFlow</a>
        <p>Advanced Reasoning AI for the Plaintiff-Side Revolution. Automating intake, discovery, and litigation intelligence.</p>
      </div>
      <div class="footer-col">
        <h4>Products</h4>
        <ul>
          <li><a href="/ai-legal-intake-software">AI Intake Agent</a></li>
          <li><a href="/voice-ai-receptionist">Voice AI Receptionist</a></li>
          <li><a href="/ai-medical-chronologies">Medical Chronologies</a></li>
          <li><a href="/auto-document-drafter">Auto-Doc Drafter</a></li>
          <li><a href="/discovery-vault">Discovery-Vault™</a></li>
          <li><a href="/settlement-predictor">Settlement-Predictor Pro™</a></li>
          <li><a href="/veritas">Veritas Deposition™</a></li>
          <li><a href="/compliance-shield">Compliance-Shield™</a></li>
          <li><a href="/dashboard">Analytics Dashboard</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>State Ethics Guides</h4>
        <ul>
          <li><a href="/blog/new-york-trial-lawyers-ai-ethics-legal-intake">New York AI Ethics</a></li>
          <li><a href="/blog/illinois-trial-lawyers-ai-ethics-legal-intake">Illinois AI Ethics</a></li>
          <li><a href="/blog/pennsylvania-trial-lawyers-ai-ethics-legal-intake">Pennsylvania AI Ethics</a></li>
          <li><a href="/blog">All Resources</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Legal</h4>
        <ul>
          <li><a href="/privacy">Privacy Policy</a></li>
          <li><a href="/terms">Terms of Service</a></li>
          <li><a href="/soc2">SOC2 Compliance</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 LexiFlow Technologies Inc. All rights reserved. | Enterprise-Grade AI for Law Firms.</p>
    </div>
  </footer>'''

FOOTER_START = re.compile(r'<footer>')
FOOTER_END = re.compile(r'</footer>')

dirs_to_scan = [
    ROOT,
    os.path.join(ROOT, "blog"),
    os.path.join(ROOT, "hardened-suite"),
    os.path.join(ROOT, "hardened-suite", "blog"),
    os.path.join(ROOT, "resources"),
    os.path.join(ROOT, "cities"),
    os.path.join(ROOT, "case-studies"),
    os.path.join(ROOT, "hardened-suite", "resources"),
]

files_processed = 0
files_skipped = 0

for d in dirs_to_scan:
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        if not f.endswith('.html'):
            continue
        fpath = os.path.join(d, f)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
        except:
            files_skipped += 1
            continue
        
        # Find footer start
        start_match = FOOTER_START.search(content)
        if not start_match:
            files_skipped += 1
            continue
        
        end_match = FOOTER_END.search(content, start_match.start())
        if not end_match:
            files_skipped += 1
            continue
        
        # Build new content
        before_footer = content[:start_match.start()]
        after_footer = content[end_match.end():]
        new_content = before_footer + STANDARD_FOOTER + after_footer
        
        with open(fpath, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        files_processed += 1
        print(f"  OK  {os.path.relpath(fpath, ROOT)}")

print(f"\nDone: {files_processed} files updated, {files_skipped} skipped")