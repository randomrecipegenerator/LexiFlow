import os

FOOTER = """    <footer class="py-20 bg-slate-50 border-t border-slate-200">
        <div class="max-w-screen">
            <div class="grid md:grid-cols-4 gap-12 mb-16">
                <div>
                    <div class="flex items-center gap-2 mb-6">
                        <img src="/branding/logo-icon.svg" alt="LexiFlow" width="20">
                        <span class="font-bold">LexiFlow</span>
                    </div>
                    <p class="text-xs text-slate-500 leading-relaxed">Enterprise-grade AI for legal intake and lead qualification. Built for the modern attorney.</p>
                </div>
                <div>
                    <h5 class="text-[10px] font-bold text-slate-900 uppercase mb-6 tracking-widest">Platform</h5>
                    <ul class="space-y-4 text-xs text-slate-600 font-medium">
                        <li><a href="/features.html">Features</a></li>
                        <li><a href="/solutions.html">Solutions</a></li>
                        <li><a href="/roi-calculator.html">ROI Calculator</a></li>
                        <li><a href="/cities.html">Service Areas</a></li>
                    </ul>
                </div>
                <div>
                    <h5 class="text-[10px] font-bold text-slate-900 uppercase mb-6 tracking-widest">Legal</h5>
                    <ul class="space-y-4 text-xs text-slate-600 font-medium">
                        <li><a href="/privacy.html">Privacy Policy</a></li>
                        <li><a href="/terms.html">Terms of Service</a></li>
                        <li><a href="#">SOC2 Compliance</a></li>
                    </ul>
                </div>
                <div>
                    <h5 class="text-[10px] font-bold text-slate-900 uppercase mb-6 tracking-widest">Security</h5>
                    <div class="flex gap-4 text-slate-300 text-xl">
                        <i class="bi bi-shield-lock"></i>
                        <i class="bi bi-safe"></i>
                        <i class="bi bi-fingerprint"></i>
                    </div>
                </div>
            </div>
            <div class="pt-8 border-t border-slate-200 flex justify-between items-center">
                <p class="text-[10px] font-bold text-slate-400 uppercase">&copy; 2026 LexiFlow AI. All rights reserved.</p>
                <div class="flex gap-6 text-slate-400">
                    <a href="#" class="hover:text-blue"><i class="bi bi-linkedin"></i></a>
                    <a href="#" class="hover:text-blue"><i class="bi bi-twitter-x"></i></a>
                </div>
            </div>
        </div>
    </footer>"""

FILES = [
    "index.html",
    "features.html",
    "solutions.html",
    "roi-calculator.html",
    "privacy.html",
    "terms.html",
    "whitepaper.html",
    "cities.html",
]

# We don't want to mess up dashboard.html or portal.html which might have special footers
# but let's check them.

def update_footers():
    for filename in FILES:
        path = f"/home/team/shared/lexiflow-mvp/{filename}"
        if not os.path.exists(path):
            continue
            
        with open(path, "r") as f:
            content = f.read()
            
        # Find footer and replace it
        if "<footer" in content and "</footer>" in content:
            start = content.find("<footer")
            end = content.find("</footer>") + len("</footer>")
            new_content = content[:start] + FOOTER + content[end:]
            
            with open(path, "w") as f:
                f.write(new_content)
            print(f"Updated footer in {filename}")

if __name__ == "__main__":
    update_footers()
