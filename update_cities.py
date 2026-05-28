import os
import glob
import re

CITIES_DIR = "/home/team/shared/lexiflow-mvp/cities"

# Comprehensive screenshot section
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
        </section>
"""

# Case study section (the one from nyc.html)
CASE_STUDY_SECTION = """
        <section class="py-12 bg-slate-50">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex flex-col md:flex-row items-center justify-between gap-8 p-8 bg-white rounded-3xl border border-slate-200 shadow-sm">
                    <div>
                        <h3 class="text-2xl font-bold mb-2">Proven Results for Top Firms</h3>
                        <p class="text-slate-600">See how Clifford Law and Smith LaCien are using LexiFlow to transform their practice.</p>
                    </div>
                    <div class="flex gap-4">
                        <a href="/marketing/case-study-clifford-law.md" class="bg-blue-600 text-white px-6 py-2 rounded-full text-sm font-semibold hover:bg-blue-700 transition" style="text-decoration: none;">Clifford Law Case Study</a>
                        <a href="/marketing/case-study-smith-lacien.md" class="bg-slate-100 text-slate-700 px-6 py-2 rounded-full text-sm font-semibold hover:bg-slate-200 transition" style="text-decoration: none;">Smith LaCien Case Study</a>
                    </div>
                </div>
            </div>
        </section>
"""

def update_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Skip nyc.html as it is the gold standard (or already has everything)
    if 'nyc.html' in filepath:
        return False

    changed = False

    # 1. Replace the simple dashboard section with the gallery
    if 'See the Attorney Dashboard in Action' not in content:
        # We want to replace the section that contains attorney-dashboard.png
        # Find the section tag that contains the image
        # Most of them look like:
        # <section class="py-20 bg-white border-t border-slate-100">
        #   ...
        #   <img src="/screenshots/attorney-dashboard.png" ...>
        #   ...
        # </section>
        pattern = r'<section class="py-20 bg-white border-t border-slate-100">.*?attorney-dashboard\.png.*?</section>'
        new_content = re.sub(pattern, SCREENSHOT_SECTION, content, flags=re.DOTALL)
        if new_content != content:
            content = new_content
            changed = True
    
    # 2. Add product card images if missing
    # MeritScan
    if 'MeritScan' in content and 'meritscan-negligence-marker.svg' not in content:
        if 'href="/meritscan.html"' in content:
            old = '<a href="/meritscan.html" class="text-emerald-600 font-semibold hover:text-emerald-700 transition">Learn More →</a>'
            new = old + '\n                        <div class="mt-4 pt-4 border-t border-slate-100">\n                            <img src="/branding/product-graphics/meritscan-negligence-marker.svg" alt="MeritScan AI Medical Merit Review" class="w-full rounded-xl border border-slate-200" loading="lazy">\n                        </div>'
            content = content.replace(old, new)
            changed = True

    # DepoLens
    if 'DepoLens' in content and 'depolens-witness-conflict.svg' not in content:
        if 'href="/depolens"' in content:
            old = '<a href="/depolens" class="text-cyan-600 font-semibold hover:text-cyan-700 transition">Learn More →</a>'
            new = old + '\n                        <div class="mt-4 pt-4 border-t border-slate-100">\n                            <img src="/branding/product-graphics/depolens-witness-conflict.svg" alt="DepoLens AI Deposition Analysis" class="w-full rounded-xl border border-slate-200" loading="lazy">\n                        </div>'
            content = content.replace(old, new)
            changed = True

    # 3. Add portal link in CTA if missing
    if 'Secure Client Portal' not in content and '/portal' in content:
        # Look for the CTA section
        if '<div class="flex flex-col sm:flex-row justify-center gap-4">' in content:
            # We'll add it after the closing </div> of the gap-4 div
            # Use regex to find the first occurrence in the CTA section
            pattern = r'(<div class="flex flex-col sm:flex-row justify-center gap-4">.*?</div>)'
            portal_cta = """
                        <div class="mt-6">
                            <a href="/portal" class="inline-flex items-center gap-2 text-blue-100 font-semibold hover:text-white transition">
                                <i class="bi bi-shield-lock-fill"></i> Secure Client Portal — Upload Documents
                            </a>
                        </div>"""
            # We only want to replace the one in the blue-600 section if possible
            # But let's keep it simple for now.
            new_content = re.sub(pattern, r'\1' + portal_cta, content, count=1, flags=re.DOTALL)
            if new_content != content:
                content = new_content
                changed = True

    # 4. Ensure case study section is at the bottom before footer
    if 'Proven Results for Top Firms' not in content:
        if '</main>' in content:
            content = content.replace('</main>', CASE_STUDY_SECTION + '\n</main>')
            changed = True

    if changed:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")
        return True
    return False

files = sorted(glob.glob(os.path.join(CITIES_DIR, "*.html")))
count = 0
for f in files:
    if update_file(f):
        count += 1

print(f"Total files updated: {count}")
