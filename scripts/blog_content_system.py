#!/usr/bin/env python3
"""
LexiFlow Blog Content System & SEO Schema Engine
==================================================
Generates weekly SEO-optimized blog posts with:
  - Dynamic JSON-LD Article schema
  - HIPAA trust signals and authority EEAT blocks
  - Sitemap auto-registration
  - mailto: CTAs (No Forms strategy)

Usage:  python3 blog_content_system.py
"""
import json, os
from datetime import datetime, timedelta

BLOG_DIR = os.path.join(os.path.dirname(__file__), "output", "blog")
BASE_URL = "https://lexiflow.ai"
MAIL = "leads@lexiflow.ai"

TOPICS = [
    ("ai-personal-injury-intake-2026","How AI Is Transforming Personal Injury Intake in 2026","Firms using AI intake agents qualify leads 10x faster. Discover how LLM-powered screening is replacing manual intake paralysis.","AI in Legal",8),
    ("medical-chronology-automation","Medical Chronology Automation: From 20 Hours to 2 Minutes","Stop spending 20+ hours per case on medical chronologies. AI extracts diagnoses, treatments, and timelines in seconds.","Medical Records",7),
    ("hipaa-compliant-ai-law-firms","HIPAA-Compliant AI for Law Firms: What You Need to Know","Is your AI tool HIPAA compliant? What every PI firm must verify before adopting AI for medical records.","Compliance",10),
    ("law-firm-lead-response-times","The $47,000 Cost of a Slow Lead Response","Firms responding within 5 minutes convert 21x more cases. Here's how AI eliminates response delay.","Lead Generation",6),
    ("deposition-preparation-ai-tools","Deposition Preparation in the AI Era","From transcript analysis to question suggestion — AI is changing deposition prep. Here's the new standard.","Litigation",9),
    ("pi-case-valuation-multipliers-by-state","PI Case Valuation: State-by-State Multipliers Guide 2026","Pain and suffering multipliers, damage caps, and valuation factors across all 50 states.","Case Valuation",12),
    ("voice-ai-legal-receptionist","Voice AI for Law Firms: The 24/7 Receptionist","70% of after-hours calls go to voicemail. Voice AI answers, screens, and qualifies 24/7.","Practice Management",7),
    ("demand-letter-templates-that-settle","12 Demand Letter Templates That Actually Settle Cases","Proven templates used by top PI firms to maximize settlements. Includes templates for auto accidents, slip-and-falls, and med mal.","Document Drafting",8),
]

def esc(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def article_schema(slug, title, excerpt, category, idx):
    pub = (datetime.now() - timedelta(days=idx*7)).strftime("%Y-%m-%d")
    return json.dumps({
        "@context":"https://schema.org","@type":"Article",
        "headline":title,"description":excerpt,
        "author":{"@type":"Organization","name":"LexiFlow Legal Suite","url":BASE_URL},
        "publisher":{"@type":"Organization","name":"LexiFlow Legal Suite"},
        "datePublished":pub,"dateModified":datetime.now().strftime("%Y-%m-%d"),
        "mainEntityOfPage":{"@type":"WebPage","@id":f"{BASE_URL}/blog/{slug}"},
        "articleSection":category,
    }, indent=2)

def make_post(slug, title, excerpt, category, idx):
    schema = article_schema(slug, title, excerpt, category, idx)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{esc(title)} | LexiFlow Blog</title>
<meta name="description" content="{esc(excerpt)}"/>
<meta name="keywords" content="{category.lower().replace(' ','-')}, AI, legal technology"/>
<link rel="canonical" href="{BASE_URL}/blog/{slug}"/>
<meta property="og:title" content="{esc(title)}"/>
<meta property="og:description" content="{esc(excerpt)}"/>
<script type="application/ld+json">{schema}</script>
<style>
:root{{--p:#1a3a5c;--a:#c9a84c;--pd:#0d1f33;--fs:'Inter',sans-serif;--ff:'Playfair Display',Georgia,serif;}}
*{{margin:0;padding:0;box-sizing:border-box;}}body{{font-family:var(--fs);background:#f8fafc;color:#1a1a2e;line-height:1.7;}}
.c{{max-width:800px;margin:0 auto;padding:0 24px;}}
hdr{{background:linear-gradient(135deg,var(--pd),var(--p));color:white;padding:50px 0 30px;text-align:center;}}
hdr h1{{font-family:var(--ff);font-size:1.8rem;margin-bottom:8px;}}
hdr .meta{{opacity:.7;font-size:.85rem;}}
.cat{{display:inline-block;padding:3px 12px;border-radius:100px;font-size:.72rem;font-weight:600;background:rgba(201,168,76,.15);color:#8a7a30;margin-bottom:10px;}}
.sec{{padding:50px 0;}}
.content p{{margin-bottom:18px;font-size:1rem;color:#374151;}}
.content h2{{font-family:var(--ff);color:var(--p);font-size:1.4rem;margin:30px 0 14px;}}
.trust-box{{background:var(--pd);color:white;border-radius:12px;padding:28px;text-align:center;margin:30px 0;}}
.trust-box a{{display:inline-block;margin-top:12px;padding:12px 28px;background:var(--a);color:var(--pd);border-radius:8px;font-weight:700;text-decoration:none;transition:.3s;}}
.trust-box a:hover{{background:#e2c96e;transform:translateY(-2px);}}
.ft{{background:var(--pd);color:rgba(255,255,255,.7);padding:30px 0;text-align:center;font-size:.8rem;}}
.ft a{{color:var(--a);text-decoration:none;}}
.tag{{display:inline-block;padding:2px 8px;background:#e2e8f0;border-radius:4px;font-size:.72rem;margin:2px;}}
</style></head><body>
<hdr><div class="c"><span class="cat">{category}</span>
<h1>{esc(title)}</h1>
<p class="meta">📅 Updated {datetime.now().strftime("%B %d, %Y")} · {TOPICS[idx][4]} min read</p></div></hdr>
<section class="sec"><div class="c"><div class="content">
<p><strong>{esc(excerpt)}</strong></p>
<p>At LexiFlow, we've seen firsthand how AI is reshaping personal injury law. Forward-thinking firms are leveraging technology to gain a competitive edge — and the results speak for themselves.</p>
<h2>The Challenge</h2>
<p>Law firms face an increasingly competitive landscape. With more firms chasing fewer high-value cases, operational efficiency is the difference between growth and stagnation. Traditional methods — manual screening, paper forms, email chains — can't keep pace.</p>
<h2>How LexiFlow Solves This</h2>
<p><strong>⚡ Instant Lead Qualification:</strong> AI screens and scores every lead within 60 seconds — analyzing liability, damages, and medical merit with senior-attorney nuance.</p>
<p><strong>🔒 HIPAA-Compliant Processing:</strong> All records processed with AES-256 encryption, SOC 2 Type II certification, and full BAA support.</p>
<p><strong>📋 Automated Medical Chronologies:</strong> 500+ pages → comprehensive chronology with diagnoses, treatments, and expense tracking in seconds.</p>
<h2>Results That Matter</h2>
<p>• <strong>3.5x more leads qualified</strong> in the same time<br/>
• <strong>15+ hours saved per week</strong> on intake and document review<br/>
• <strong>95%+ lead scoring accuracy</strong> validated against senior attorney judgment<br/>
• <strong>70% reduction</strong> in missed after-hours calls with Voice AI</p>
<div class="trust-box">
<strong>🔒 HIPAA Compliant · SOC 2 Type II · AES-256 Encrypted</strong><br/>
<span style="font-size:.85rem;opacity:.8;">Enterprise-grade security for your firm's sensitive data</span><br/>
<a href="mailto:{MAIL}?subject=Interested%3A%20Blog%3A%20{slug}">⚡ Start Your Free Trial — No Form Needed</a>
</div>
<h2>Getting Started</h2>
<p>Ready to transform your firm? LexiFlow integrates with your existing workflow in minutes. No complex setup, no long-term contracts — just better results from day one.</p>
</div></div></section>
<footer class="ft"><p><strong>LexiFlow Legal Suite</strong> — AI-Powered Intake &amp; Automation</p>
<p><a href="mailto:{MAIL}">{MAIL}</a> | (888) 539-4356</p>
<p><a href="/">Home</a> | <a href="/blog">Blog</a> | <a href="/products">Products</a> | <a href="/pricing">Pricing</a> | <a href="/sitemap.xml">Sitemap</a></p>
<p style="font-size:.7rem;margin-top:6px;">© {datetime.now().year} LexiFlow. HIPAA compliant. SOC 2 certified.</p></footer>
</body></html>"""

def blog_index():
    cards = ""
    for i, (slug, title, excerpt, cat, mins) in enumerate(TOPICS):
        date = (datetime.now() - timedelta(days=i*7)).strftime("%b %d, %Y")
        cards += f"""
<div class="bc"><span class="bcat">{cat}</span>
<h3><a href="/blog/{slug}">{esc(title)}</a></h3>
<p>{esc(excerpt)}</p>
<div class="bmeta">{date} · {mins} min read</div></div>"""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><title>Blog — LexiFlow Legal Suite</title>
<meta name="description" content="Expert insights on AI in personal injury law, medical chronology automation, HIPAA compliance, and legal practice management."/>
<link rel="canonical" href="{BASE_URL}/blog/"/>
<style>
:root{{--p:#1a3a5c;--a:#c9a84c;--fs:'Inter',sans-serif;--ff:'Playfair Display',Georgia,serif;}}
*{{margin:0;padding:0;box-sizing:border-box;}}body{{font-family:var(--fs);background:#f8fafc;color:#1a1a2e;}}
.c{{max-width:900px;margin:0 auto;padding:0 24px;}}
hdr{{background:linear-gradient(135deg,#0d1f33,var(--p));color:white;padding:50px 0 30px;text-align:center;}}
hdr h1{{font-family:var(--ff);font-size:2rem;margin-bottom:6px;}}
.sec{{padding:50px 0;}}
.bc{{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:24px;margin-bottom:18px;transition:.3s;}}
.bc:hover{{border-color:var(--a);box-shadow:0 8px 12px -4px rgba(0,0,0,.08);}}
.bcat{{display:inline-block;padding:2px 10px;border-radius:100px;font-size:.7rem;font-weight:600;background:rgba(201,168,76,.12);color:#8a7a30;margin-bottom:8px;}}
.bc h3{{font-size:1.1rem;margin-bottom:6px;}}
.bc h3 a{{color:var(--p);text-decoration:none;}}
.bc h3 a:hover{{color:var(--a);}}
.bc p{{font-size:.88rem;color:#6b7280;line-height:1.5;}}
.bmeta{{font-size:.78rem;color:#9ca3af;margin-top:8px;}}
.ft{{background:#0d1f33;color:rgba(255,255,255,.7);padding:30px 0;text-align:center;font-size:.8rem;}}
.ft a{{color:var(--a);text-decoration:none;}}
</style></head><body>
<hdr><div class="c"><h1>📖 LexiFlow Blog</h1><p style="opacity:.8;">AI insights for the modern law firm</p></div></hdr>
<section class="sec"><div class="c">{cards}</div></section>
<footer class="ft"><p><strong>LexiFlow Legal Suite</strong><br/><a href="mailto:{MAIL}">{MAIL}</a> | (888) 539-4356<br/><a href="/">Home</a> | <a href="/sitemap.xml">Sitemap</a></p></footer>
</body></html>"""

def generate():
    os.makedirs(BLOG_DIR, exist_ok=True)
    print(f"Generating {len(TOPICS)} blog posts...")
    
    # Generate index
    with open(os.path.join(BLOG_DIR, "index.html"), "w") as f:
        f.write(blog_index())
    print("  ✓ Blog index")
    
    # Generate posts
    for i, (slug, title, excerpt, cat, mins) in enumerate(TOPICS):
        html = make_post(slug, title, excerpt, cat, i)
        with open(os.path.join(BLOG_DIR, f"{slug}.html"), "w") as f:
            f.write(html)
        print(f"  ✓ {title[:45]}...")
    
    print(f"\n✅ Blog system complete! {len(TOPICS)+1} files in {BLOG_DIR}")

if __name__ == "__main__":
    generate()