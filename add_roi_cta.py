#!/usr/bin/env python3
"""Add ROI Calculator CTA to all city pages (handles permission issues)."""
import os, glob, sys

CITIES_DIR = "/home/team/shared/lexiflow-mvp/cities"
ROI_LINK = '\n                    <a href="/roi-calculator" class="inline-flex items-center gap-2 text-blue-100 font-semibold hover:text-white transition text-sm mt-2">\n                        <i class="bi bi-calculator"></i> Calculate Your Firm\'s AI ROI →\n                    </a>'

count = 0
for f in sorted(glob.glob(os.path.join(CITIES_DIR, "*.html"))):
    try:
        with open(f) as fh:
            content = fh.read()
    except PermissionError:
        print(f"  ⛔ Permission denied: {os.path.basename(f)}")
        continue
    
    if 'Calculate Your Firm' in content or '/roi-calculator' in content:
        print(f"  ⏭️ Already has ROI CTA: {os.path.basename(f)}")
        continue
    
    # Add ROI link before the closing div of the CTA section (before decorative circles)
    old = 'class="bg-white text-blue-600 px-8 py-4 rounded-xl font-bold hover:bg-blue-50 transition text-lg">Request a Demo</button>'
    if old in content:
        new = old + ROI_LINK
        content = content.replace(old, new, 1)
    else:
        # Try alternative CTA button text
        old2 = 'class="bg-white text-blue-600 px-8 py-4 rounded-xl font-bold hover:bg-blue-50 transition text-lg">Request Consultation</button>'
        if old2 in content:
            new = old2 + ROI_LINK
            content = content.replace(old2, new, 1)
    
    if 'Calculate Your Firm' in content:
        try:
            with open(f, "w") as fh:
                fh.write(content)
            count += 1
            print(f"  ✅ Updated: {os.path.basename(f)}")
        except PermissionError:
            print(f"  ⛔ Write denied: {os.path.basename(f)}")

print(f"\nDone! Updated {count} city pages with ROI Calculator CTA.")