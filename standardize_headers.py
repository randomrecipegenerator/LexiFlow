#!/usr/bin/env python3
"""Replace all nav headers in LexiFlow HTML files with the standard header."""
import os, re

ROOT = "/home/team/shared/LexiFlow-Final"

# The standard header (unindented — we dedent it)
STANDARD = '''<body><nav><div class="nav-container">
    <a href="/" class="logo"><span>LF</span> LexiFlow</a>
    <ul class="nav-links" id="navLinks">
      <li><a href="/pricing">Pricing</a></li>
      <li><a href="/solutions">Solutions</a></li>
      <li><a href="/dashboard">Dashboard</a></li>
      <li><a href="/blog">Blog</a></li>
      <li class="resources-dropdown">
        <a href="#">Resources ▾</a>
        <div class="resources-menu">
          <a href="/resources/medical-chronology-template">Medical Chronology Template</a>
          <a href="/resources/medical-chronology-sample">Medical Chronology Sample</a>
          <a href="/resources/medical-record-review-checklist">Record Review Checklist</a>
          <a href="/ssd-disability-medical-chronology-software">SSD & Disability AI</a>
          <a href="/witness-testimony-analysis">Witness Testimony Analysis</a>
          <a href="/case-studies">Case Studies</a>
        </div>
      </li>
      <li><a href="/roi-calculator">ROI Calculator</a></li>
      <li><a href="/login">Log In</a></li>
      <li><a href="/signup" class="btn-cta">Get Started</a></li>
    </ul>
    <button class="nav-toggle" aria-label="Menu">☰</button>
  </div></nav>'''

# Pattern: from `<nav><div class="nav-container">` to `</div></nav>`
NAV_START = re.compile(r'<body><nav><div class="nav-container">')
NAV_END = re.compile(r'</div></nav>')

dirs_to_scan = [
    ROOT,
    os.path.join(ROOT, "blog"),
    os.path.join(ROOT, "hardened-suite"),
    os.path.join(ROOT, "hardened-suite", "blog"),
    os.path.join(ROOT, "hardened-suite", "resources"),
    os.path.join(ROOT, "cities"),
    os.path.join(ROOT, "resources"),
    os.path.join(ROOT, "case-studies"),
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
        
        # Find start and end of nav
        start_match = NAV_START.search(content)
        if not start_match:
            files_skipped += 1
            continue
        
        end_match = NAV_END.search(content, start_match.start())
        if not end_match:
            files_skipped += 1
            continue
        
        # Build new content
        before_nav = content[:start_match.start()]
        after_nav = content[end_match.end():]
        new_content = before_nav + STANDARD + after_nav
        
        with open(fpath, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        files_processed += 1
        print(f"  OK  {os.path.relpath(fpath, ROOT)}")

print(f"\nDone: {files_processed} files updated, {files_skipped} skipped")