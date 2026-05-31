#!/usr/bin/env python3
"""
LexiFlow National Expansion Engine v3
=======================================
Generates 99 city-specific landing pages with:
- HIPAA compliance trust signals
- JSON-LD schema (Organization, LocalBusiness, Article)
- No Forms strategy (all mailto: CTAs)
- 6 lead magnets per city
- Dynamic sitemap.xml with ~120 URLs
- SEO-optimized blog system

Usage:  python3 national_expansion_engine.py
"""
import json, os
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
BASE_URL = "https://lexiflow.ai"
MAIL = "leads@lexiflow.ai"
PHONE = "(888) 539-4356"
YEAR = datetime.now().year

CITIES = [
    ("New York","NY"),("Los Angeles","CA"),("Chicago","IL"),("Houston","TX"),
    ("Phoenix","AZ"),("Philadelphia","PA"),("San Antonio","TX"),("San Diego","CA"),
    ("Dallas","TX"),("San Jose","CA"),("Austin","TX"),("Jacksonville","FL"),
    ("Fort Worth","TX"),("Columbus","OH"),("Charlotte","NC"),("Indianapolis","IN"),
    ("San Francisco","CA"),("Seattle","WA"),("Denver","CO"),("Nashville","TN"),
    ("Oklahoma City","OK"),("El Paso","TX"),("Washington","DC"),("Boston","MA"),
    ("Memphis","TN"),("Portland","OR"),("Louisville","KY"),("Milwaukee","WI"),
    ("Baltimore","MD"),("Albuquerque","NM"),("Tucson","AZ"),("Fresno","CA"),
    ("Sacramento","CA"),("Kansas City","MO"),("Long Beach","CA"),("Mesa","AZ"),
    ("Atlanta","GA"),("Colorado Springs","CO"),("Virginia Beach","VA"),("Raleigh","NC"),
    ("Omaha","NE"),("Miami","FL"),("Oakland","CA"),("Minneapolis","MN"),
    ("Tulsa","OK"),("Wichita","KS"),("New Orleans","LA"),("Arlington","TX"),
    ("Cleveland","OH"),("Bakersfield","CA"),("Tampa","FL"),("Anaheim","CA"),
    ("Honolulu","HI"),("Aurora","CO"),("Santa Ana","CA"),("St. Louis","MO"),
    ("Riverside","CA"),("Corpus Christi","TX"),("Pittsburgh","PA"),("Lexington","KY"),
    ("Stockton","CA"),("Cincinnati","OH"),("St. Paul","MN"),("Toledo","OH"),
    ("Newark","NJ"),("Greensboro","NC"),("Plano","TX"),("Henderson","NV"),
    ("Lincoln","NE"),("Buffalo","NY"),("Jersey City","NJ"),("Chula Vista","CA"),
    ("Fort Wayne","IN"),("Orlando","FL"),("St. Petersburg","FL"),("Chandler","AZ"),
    ("Laredo","TX"),("Norfolk","VA"),("Durham","NC"),("Madison","WI"),
    ("Lubbock","TX"),("Irvine","CA"),("Winston-Salem","NC"),("Glendale","AZ"),
    ("Garland","TX"),("Scottsdale","AZ"),("Boise","ID"),("Birmingham","AL"),
    ("Baton Rouge","LA"),("Des Moines","IA"),("Anchorage","AK"),("Rochester","NY"),
    ("Richmond","VA"),("Spokane","WA"),("Providence","RI"),("Las Vegas","NV"),
    ("Salt Lake City","UT"),("Charleston","SC"),("Knoxville","TN"),("Grand Rapids","MI"),
]

LEAD_MAGNETS = [
    ("intake-leakage-audit","Intake Leakage Audit","Find out where your firm loses cases","🔍"),
    ("missed-call-report","After-Hours Missed Call Report","Every missed call costs money","📞"),
    ("sample-chronology","Sample AI Chronology Report","See AI-generated medical chronologies","📋"),
    ("demand-letter-pack","Winning Demand Letter Template Pack","Proven settlement templates","✉️"),
    ("depo-checklist","The 2026 Depo Preparation Checklist","Never miss a critical question","📝"),
    ("case-valuation-sheet","PI Case Valuation Cheat Sheet","Value any PI case in minutes","💰"),
]

PRODUCTS = [
    ("AI Intake Agent","ai-intake-agent","24/7 AI-powered intake"),
    ("Voice AI Receptionist","voice-ai-receptionist","Never miss a call"),
    ("AI Medical Chronologies","ai-medical-chronologies","500+ pages in seconds"),
    ("Auto-Document Drafter","auto-document-drafter","AI drafts demand letters"),
    ("DepoLens AI","depolens-ai","AI deposition analysis"),
    ("Settlement Estimator","settlement-estimator","PI case valuation"),
]

BLOG_POSTS = [
    ("ai-personal-injury-intake-2026","How AI Is Transforming PI Intake","Firms qualify leads 10x faster","AI in Legal"),
    ("medical-chronology-automation","Medical Chronology Automation","From 20 hours to 2 minutes","Medical Records"),
    ("hipaa-compliant-ai-law-firms","HIPAA-Compliant AI for Law Firms","What every firm must verify","Compliance"),
    ("law-firm-lead-response-times","The Cost of Slow Lead Response","5 min = 21x more conversions","Lead Gen"),
    ("deposition-preparation-ai","Deposition Prep in the AI Era","AI-transcript analysis","Litigation"),
    ("pi-case-valuation-guide","PI Case Valuation Guide","State-by-state multipliers","Valuation"),
    ("voice-ai-legal-receptionist","Voice AI for Law Firms","24/7 AI receptionist","Practice Mgmt"),
    ("demand-letter-templates","Demand Letter Templates","Proven settlement templates","Drafting"),
]

def sl(s): return s.lower().replace(" ","-").replace(".","").replace("'","")
def h(s): return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def gen_city(city, state):
    s = sl(city); d = f"{city}, {state}"
    org = json.dumps({"@context":"https://schema.org","@graph":[
        {"@type":"Organization","name":"LexiFlow Legal Suite","url":BASE_URL,"email":MAIL,"address":{"@type":"PostalAddress","addressLocality":city,"addressRegion":state,"addressCountry":"US"}},
        {"@type":"LocalBusiness","name":f"LexiFlow — {d}","telephone":PHONE,"areaServed":{"@type":"City","name":city}},
    ]}, indent=2)
    mc = "".join(f'<div class="mc"><div class="mi">{ic}</div><h3>{h(n)}</h3><p>{h(t)}</p><a href="mailto:{MAIL}?subject={h(n)}%20-%20{slug(ic)}" class="mb">Get →</a></div>' for iid,n,t,ic in LEAD_MAGNETS)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"/><title>AI Legal Tools for {h(d)}|LexiFlow</title>
<meta name="description" content="AI intake, chronologies, drafting for {h(d)}. HIPAA compliant."/>
<link rel="canonical" href="{BASE_URL}/{s}"/><meta name="geo.region" content="US-{state}"/>
<script type="application/ld+json">{org}</script>
<style>:root{{--p:#1a3a5c;--a:#c9a84c;--pd:#0d1f33;--fs:'Inter',sans-serif;}}*{{margin:0;padding:0;}}body{{font-family:var(--fs);background:#f8fafc;color:#1a1a2e;line-height:1.6;}}.c{{max-width:1100px;margin:0 auto;padding:0 24px;}}.hero{{padding:80px 0;background:linear-gradient(135deg,var(--pd),var(--p));color:white;text-align:center;}}.hero h1{{font-size:2.2rem;margin-bottom:12px;}}.hero .ac{{color:var(--a);}}.tb{{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-bottom:24px;}}.tb span{{padding:4px 12px;border-radius:100px;font-size:.72rem;background:rgba(255,255,255,.12);}}.cb{{display:inline-block;padding:14px 32px;background:var(--a);color:var(--pd);border-radius:10px;font-weight:700;text-decoration:none;}}.mg{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;}}@media(max-width:768px){{.mg{{grid-template-columns:1fr;}}}}.mc{{background:white;border:1px solid #e2e8f0;border-radius:12px;padding:22px;text-align:center;}}.mi{{font-size:2rem;}}.mc h3{{font-size:.95rem;color:var(--p);}}.mb{{display:inline-block;padding:8px 16px;background:var(--p);color:white;border-radius:6px;text-decoration:none;}}.sec{{padding:50px 0;}}.sec h2{{text-align:center;color:var(--p);margin-bottom:30px;}}.ft{{background:var(--pd);color:rgba(255,255,255,.7);padding:30px 0;text-align:center;font-size:.8rem;}}.ft a{{color:var(--a);}}</style></head><body>
<section class="hero"><div class="c"><div class="tb"><span>✓ HIPAA</span><span>✓ SOC 2</span><span>✓ Encrypted</span><span>✓ BAA</span></div>
<h1>AI Legal Tools for <span class="ac">{h(d)}</span></h1><p>Qualify leads 10x faster, save 15+ hrs/week.</p>
<a href="mailto:{MAIL}?subject=Interested%20{city}" class="cb">⚡ Start Free Trial (No Form)</a></div></section>
<section class="sec"><div class="c"><h2>Free Resources</h2><div class="mg">{mc}</div></div></section>
<footer class="ft"><p><strong>LexiFlow</strong><br/><a href="mailto:{MAIL}">{MAIL}</a> | {PHONE}<br/><a href="/sitemap.xml">Sitemap</a> | © {YEAR}</p></footer>
</body></html>"""

def gen_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True); os.makedirs(os.path.join(OUTPUT_DIR,"blog"), exist_ok=True)
    for c,s in CITIES:
        with open(os.path.join(OUTPUT_DIR,f"{sl(c)}.html"),"w") as f: f.write(gen_city(c,s))
    for slug,t,e,cat in BLOG_POSTS:
        schema=json.dumps({"@context":"https://schema.org","@type":"Article","headline":t,"description":e,"author":{"@type":"Organization","name":"LexiFlow"},"datePublished":datetime.now().strftime("%Y-%m-%d")})
        fp=os.path.join(OUTPUT_DIR,"blog",f"{slug}.html")
        with open(fp,"w") as f: f.write(f'<!DOCTYPE html><html><head><meta charset="UTF-8"/><title>{h(t)}|LexiFlow</title><meta name="description" content="{h(e)}"/><link rel="canonical" href="{BASE_URL}/blog/{slug}"/><script type="application/ld+json">{schema}</script><style>:root{{--p:#1a3a5c;--a:#c9a84c;--pd:#0d1f33;--fs:"Inter",sans-serif;}}*{{margin:0;padding:0;}}body{{font-family:var(--fs);color:#1a1a2e;}}.c{{max-width:800px;margin:0 auto;padding:0 24px;}}hdr{{background:linear-gradient(135deg,var(--pd),var(--p));color:white;padding:50px 0;text-align:center;}}.tb{{background:var(--pd);color:white;border-radius:12px;padding:28px;text-align:center;margin:30px 0;}}.tb a{{display:inline-block;padding:12px 28px;background:var(--a);color:var(--pd);border-radius:8px;font-weight:700;text-decoration:none;}}</style></head><body><hdr><div class="c"><h1>{h(t)}</h1></div></hdr><section style="padding:50px 0;"><div class="c"><p>{h(e)}</p><div class="tb"><a href="mailto:{MAIL}?subject=Blog%20{slug}">⚡ Start Free Trial</a></div></div></section></body></html>')
    cards="".join(f'<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:20px;margin-bottom:16px;"><h3><a href="/blog/{s}" style="color:#1a3a5c;">{h(t)}</a></h3><p style="color:#6b7280;">{h(e)}</p></div>' for s,t,e,cat in BLOG_POSTS)
    with open(os.path.join(OUTPUT_DIR,"blog","index.html"),"w") as f: f.write(f'<!DOCTYPE html><html><head><meta charset="UTF-8"/><title>LexiFlow Blog</title></head><body><h1>📖 LexiFlow Blog</h1><section>{cards}</section></body></html>')
    urls=[f'<url><loc>{BASE_URL}/</loc><priority>1.0</priority></url>']
    for _,s,_ in PRODUCTS: urls.append(f'<url><loc>{BASE_URL}/{s}</loc><priority>0.9</priority></url>')
    for c,_ in CITIES: urls.append(f'<url><loc>{BASE_URL}/{sl(c)}</loc><priority>0.7</priority></url>')
    for s,_,_,_ in BLOG_POSTS: urls.append(f'<url><loc>{BASE_URL}/blog/{s}</loc><priority>0.8</priority></url>')
    with open(os.path.join(OUTPUT_DIR,"sitemap.xml"),"w") as f: f.write('<?xml version="1.0"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+'\n'.join(urls)+'\n</urlset>')
    with open(os.path.join(OUTPUT_DIR,"robots.txt"),"w") as f: f.write("User-agent: *\nAllow: /\nSitemap: "+BASE_URL+"/sitemap.xml\n")
    fl=[f for f in os.listdir(OUTPUT_DIR) if f.endswith(".html")]
    print(f"✅ Generated {len(fl)} city pages + {len(BLOG_POSTS)+1} blog files + sitemap")

if __name__=="__main__":
    gen_all()