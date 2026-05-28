#!/usr/bin/env python3
"""Batch update all 20 city pages with visual assets and portal links."""

import os, glob

CITIES_DIR = "/home/team/shared/lexiflow-mvp/cities"
SVG_DIR = "/branding/product-graphics"
SCREENSHOT_DIR = "/screenshots"
PORTAL_URL = "/portal"

# Visual card to inject after the product section's "Learn More" button in each product card
VISUAL_INJECT = """
                        <!-- Product Visual -->
                        <div class="mt-4 pt-4 border-t border-slate-100">
                            <img src="{svg}" alt="{alt}" class="w-full rounded-xl border border-slate-200" loading="lazy">
                        </div>"""

# Portal CTA to inject into the CTA section
PORTAL_INJECT = """
                <div class="mt-2 text-center">
                    <a href="{portal_url}" class="inline-flex items-center gap-2 text-blue-600 font-semibold hover:text-blue-700 transition text-sm">
                        <i class="bi bi-shield-lock-fill"></i>
                        Secure Client Portal — Upload Documents
                    </a>
                </div>"""

# Dashboard screenshot section to add after features
SCREENSHOT_SECTION = """
        <!-- Dashboard Preview Section -->
        <section class="py-20 bg-white">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center mb-12">
                    <h2 class="text-3xl font-bold mb-4">See the Attorney Dashboard in Action</h2>
                    <p class="text-slate-600 max-w-2xl mx-auto">Qualified leads flow directly into your dashboard with AI-powered summaries, case scoring, and one-click CRM sync.</p>
                </div>
                <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 hover:shadow-lg transition">
                        <img src="/screenshots/attorney-dashboard.png" alt="LexiFlow Attorney Dashboard" class="w-full rounded-xl border border-slate-200" loading="lazy">
                        <p class="text-sm text-slate-500 mt-3 text-center font-medium">AI-Powered Lead Pipeline</p>
                    </div>
                    <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 hover:shadow-lg transition">
                        <img src="/screenshots/intake-chatting.png" alt="LexiFlow AI Intake Chat" class="w-full rounded-xl border border-slate-200" loading="lazy">
                        <p class="text-sm text-slate-500 mt-3 text-center font-medium">24/7 AI Intake Conversation</p>
                    </div>
                    <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 hover:shadow-lg transition">
                        <img src="/screenshots/dashboard_forms.png" alt="LexiFlow Forms Management" class="w-full rounded-xl border border-slate-200" loading="lazy">
                        <p class="text-sm text-slate-500 mt-3 text-center font-medium">Intelligent Forms Builder</p>
                    </div>
                    <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200 hover:shadow-lg transition">
                        <img src="/branding/product-graphics/meritscan-negligence-marker.svg" alt="MeritScan Negligence Detection" class="w-full rounded-xl border border-slate-200" loading="lazy">
                        <p class="text-sm text-slate-500 mt-3 text-center font-medium">AI Negligence Marker Detection</p>
                    </div>
                </div>
                <div class="text-center mt-8">
                    <a href="/dashboard" class="text-blue-600 font-semibold hover:text-blue-700 transition">View Full Dashboard Demo →</a>
                </div>
            </div>
        </section>"""

# Case study link to add to testimonial section  
CASE_STUDY_LINK = """
                <div class="mt-4 text-center">
                    <a href="/marketing/case-study-clifford-law.md" class="text-blue-600 text-sm font-semibold hover:text-blue-700 transition">
                        Read Full Case Study → <span class="text-slate-400 font-normal">(391% conversion boost)</span>
                    </a>
                </div>"""

# Portal badge for navbar
NAVBAR_PORTAL = """
                <a href="/portal" class="text-blue-600 font-semibold text-sm hover:text-blue-700 transition flex items-center gap-1">
                    <i class="bi bi-shield-lock-fill text-xs"></i> Client Portal
                </a>"""

def update_city_page(filepath):
    """Update a single city page with all visual assets."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    city_name = os.path.basename(filepath).replace('.html', '').replace('-', ' ').title()
    changes = 0
    
    # 1. Add navbar portal link (before the Get Started button)
    if 'NAVBAR_PORTAL' not in content:
        if '<div><button onclick="toggleModal' in content:
            old = '<div><button onclick="toggleModal'
            new = f'{NAVBAR_PORTAL}\n                {old}'
            content = content.replace(old, new, 1)
            changes += 1
    
    # 2. Add screenshot dashboard section after features section
    # (after the features div that uses grid md:grid-cols-2 lg:grid-cols-3 gap-8)
    if 'See the Attorney Dashboard in Action' not in content:
        # Find a closing section tag after the features grid
        pattern = '            </div>\n        </section>\n\n        <!-- CTA Section -->'
        if pattern in content:
            content = content.replace(pattern, f'        </div>\n    </section>\n    {SCREENSHOT_SECTION}\n\n        <!-- CTA Section -->', 1)
            changes += 1
    
    # 3. Add portal CTA link to the CTA section
    if 'Secure Client Portal' not in content:
        # Add after the CTA button
        cta_pattern = '<div class="flex flex-col sm:flex-row justify-center gap-4">'
        if cta_pattern in content:
            # Find the closing of the CTA section and add portal link
            old_cta_end = '                            </div>\n                        </div>'
            new_cta_end = f'                            </div>\n                            {PORTAL_INJECT}\n                        </div>'
            content = content.replace(old_cta_end, new_cta_end, 1)
            changes += 1
    
    # 4. Add case study links to testimonial blocks
    if 'Read Full Case Study' not in content and 'case-study' not in content:
        testimonial_end = '</blockquote>'
        if testimonial_end in content:
            content = content.replace(testimonial_end, f'{testimonial_end}{CASE_STUDY_LINK}', 1)
            changes += 1
    
    # 5. Add product SVGs to the product cards  
    # MeritScan card
    if 'meritscan-negligence-marker.svg' not in content:
        old_meritscan = '<a href="/meritscan.html" class="text-emerald-600 font-semibold hover:text-emerald-700 transition">Learn More →</a>\n                    </div>\n                    <div'
        new_meritscan = f'<a href="/meritscan.html" class="text-emerald-600 font-semibold hover:text-emerald-700 transition">Learn More →</a>\n                        <div class="mt-4 pt-4 border-t border-slate-100">\n                            <img src="{SVG_DIR}/meritscan-negligence-marker.svg" alt="MeritScan AI Medical Merit Review" class="w-full rounded-xl border border-slate-200" loading="lazy">\n                        </div>\n                    </div>\n                    <div'
        content = content.replace(old_meritscan, new_meritscan, 1)
        changes += 1
    
    # DepoLens card
    if 'depolens-witness-conflict.svg' not in content:
        old_depolens = '<a href="/depolens" class="text-cyan-600 font-semibold hover:text-cyan-700 transition">Learn More →</a>\n                    </div>\n                </div>'
        new_depolens = f'<a href="/depolens" class="text-cyan-600 font-semibold hover:text-cyan-700 transition">Learn More →</a>\n                        <div class="mt-4 pt-4 border-t border-slate-100">\n                            <img src="{SVG_DIR}/depolens-witness-conflict.svg" alt="DepoLens AI Deposition Analysis" class="w-full rounded-xl border border-slate-200" loading="lazy">\n                        </div>\n                    </div>\n                </div>'
        if old_depolens in content:
            content = content.replace(old_depolens, new_depolens, 1)
            changes += 1
    
    # 6. Add widget script for live demo chat (at the end before </body>)
    if 'lexi-widget' not in content:
        old_body_end = '</body>\n</html>'
        new_body_end = """    <!-- LexiFlow AI Chat Widget -->
    <script>
        (function() {
            var widget = document.createElement('script');
            widget.src = '/widget.min.js';
            widget.async = true;
            document.head.appendChild(widget);
            var css = document.createElement('link');
            css.rel = 'stylesheet';
            css.href = '/widget.min.css';
            document.head.appendChild(css);
        })();
    </script>
</body>
</html>"""
        content = content.replace(old_body_end, new_body_end, 1)
        changes += 1
    
    # Write back if changes were made
    if changes > 0:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✅ Updated {os.path.basename(filepath)} ({changes} changes)")
        return True
    else:
        print(f"  ⏭️  No changes needed for {os.path.basename(filepath)}")
        return False

# Process all city pages
print("Updating city pages with visual assets...")
total = 0
for f in sorted(glob.glob(os.path.join(CITIES_DIR, "*.html"))):
    if update_city_page(f):
        total += 1

print(f"\n🎯 Done! Updated {total} out of 20 city pages.")