#!/usr/bin/env python3
"""Apply homepage SEO changes to index.html (feature branch copy)."""
import io

path = "/home/agent-frontend-developer/lexflow-seo/index.html"
with io.open(path, encoding="utf-8") as f:
    html = f.read()

orig = html

def rep(old, new, count=1):
    global html
    n = html.count(old)
    if n == 0:
        raise SystemExit("NOT FOUND: %r" % old[:90])
    html = html.replace(old, new, count)
    return n

# 1. Title (exact owner-specified)
rep(
    "<title>LexiFlow | AI Legal Operations & Matter Management \u2014 Active Workspace</title>",
    "<title>AI Legal Assistant | Legal Help, Contract Review &amp; Research</title>",
)

# 2. Meta description (draft matching title intent; owner copy swap point)
rep(
    '<meta name="description" content="LexiFlow is AI-powered legal operations software for plaintiff firms. Automate intake, medical merit review, and deposition analysis. Experience the Rodriguez v. Mount Sinai live workspace \u2014 92/100 Merit Score, 7 flagged contradictions, $4.2M trial value." />',
    '<meta name="description" content="LexiFlow is the AI legal assistant for law firms. Get AI-powered legal help, contract review, and legal research with fast, accurate, defensible results." />',
)

# 3. Keywords
rep(
    '<meta name="keywords" content="legal operations software, AI legal intake, legal matter management, law firm automation, medical merit review, deposition analysis software, personal injury law firm software" />',
    '<meta name="keywords" content="AI legal assistant, legal help, contract review AI, legal research AI, AI lawyer, legal document analysis, legal document generator, law firm AI" />',
)

# 4. OG + Twitter tags
rep(
    '<meta property="og:title" content="LexiFlow | AI Legal Operations & Matter Management \u2014 Active Workspace" />',
    '<meta property="og:title" content="AI Legal Assistant | Legal Help, Contract Review &amp; Research" />',
)
rep(
    '<meta property="og:description" content="LexiFlow is AI-powered legal operations software for plaintiff firms. Automate intake, medical merit review, and deposition analysis. Experience the Rodriguez v. Mount Sinai live workspace \u2014 92/100 Merit Score, 7 flagged contradictions, $4.2M trial value." />',
    '<meta property="og:description" content="LexiFlow is the AI legal assistant for law firms. Get AI-powered legal help, contract review, and legal research with fast, accurate, defensible results." />',
)
rep(
    '<meta name="twitter:title" content="LexiFlow | AI Legal Operations & Matter Management \u2014 Active Workspace" />',
    '<meta name="twitter:title" content="AI Legal Assistant | Legal Help, Contract Review &amp; Research" />',
)
rep(
    '<meta name="twitter:description" content="LexiFlow is AI-powered legal operations software for plaintiff firms. Automate intake, medical merit review, and deposition analysis. Experience the Rodriguez v. Mount Sinai live workspace \u2014 92/100 Merit Score, 7 flagged contradictions, $4.2M trial value." />',
    '<meta name="twitter:description" content="LexiFlow is the AI legal assistant for law firms. Get AI-powered legal help, contract review, and legal research with fast, accurate, defensible results." />',
)

# 5. H1 — primary keyword naturally
rep(
    "<h1>AI Legal Operations &amp; Active Case Workspace \u2014 <span>Rodriguez v. Mount Sinai</span></h1>",
    "<h1>Your AI Legal Assistant &amp; Active Case Workspace \u2014 <span>Rodriguez v. Mount Sinai</span></h1>",
)

# 6. First paragraph — primary keyword naturally
rep(
    "<p>You are logged into a live case. In your dashboard, you can see an AI-qualified medical malpractice lead",
    "<p>This is what an AI legal assistant does in practice. You are logged into a live case. In your dashboard, you can see an AI-qualified medical malpractice lead",
)

# 7. One relevant H2 — primary keyword naturally
rep(
    ">Your AI-Powered Legal Operations Workspace</h2>",
    ">What Your AI Legal Assistant Automates</h2>",
)

# 8. Visible hero image with keyword-rich alt text (dashboard-hero.svg)
rep(
    '        <a href="/dashboard" style="display:block;margin-top:24px;font-size:13px;color:var(--gold);text-decoration:none;">Open full case dashboard &rarr;</a>',
    '        <a href="/dashboard" style="display:block;margin-top:24px;font-size:13px;color:var(--gold);text-decoration:none;">Open full case dashboard &rarr;</a>\n        <img src="/assets/screenshots/dashboard-hero.svg" alt="AI Legal Assistant dashboard for law firm case management" style="width:100%;margin-top:24px;border-radius:12px;border:1px solid rgba(255,255,255,0.12);" loading="lazy" />',
    1,
)

# 9. Internal links to the 7 new supporting pages in Advanced Legal AI Resources
links_block = (
    '\n      <a href="/ai-contract-review" style="color:var(--navy);text-decoration:none;font-weight:600;">AI Contract Review</a>'
    '\n      <a href="/ai-legal-research" style="color:var(--navy);text-decoration:none;font-weight:600;">AI Legal Research</a>'
    '\n      <a href="/ai-legal-document-analysis" style="color:var(--navy);text-decoration:none;font-weight:600;">AI Legal Document Analysis</a>'
    '\n      <a href="/ai-legal-document-generator" style="color:var(--navy);text-decoration:none;font-weight:600;">AI Legal Document Generator</a>'
    '\n      <a href="/ai-legal-assistant-for-lawyers" style="color:var(--navy);text-decoration:none;font-weight:600;">AI Legal Assistant for Lawyers</a>'
    '\n      <a href="/ai-legal-help" style="color:var(--navy);text-decoration:none;font-weight:600;">AI Legal Help</a>'
    '\n      <a href="/ai-lawyer" style="color:var(--navy);text-decoration:none;font-weight:600;">AI Lawyer</a>'
)
amp = '<a href="/compliance-shield" style="color:var(--navy);text-decoration:none;font-weight:600;">HIPAA &amp; SOC2 Compliance</a>'
raw = '<a href="/compliance-shield" style="color:var(--navy);text-decoration:none;font-weight:600;">HIPAA & SOC2 Compliance</a>'
if amp in html:
    html = html.replace(amp, amp + links_block, 1)
elif raw in html:
    html = html.replace(raw, raw + links_block, 1)
else:
    raise SystemExit("NOT FOUND: compliance-shield resources link")

with io.open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("OK - all replacements applied")
