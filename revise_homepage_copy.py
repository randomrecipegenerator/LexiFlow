#!/usr/bin/env python3
"""Revise homepage demo copy: de-center from Rodriguez v. Mount Sinai, target AI legal keyword set naturally."""
import io, re, json

path = "index.html"
html = io.open(path, encoding="utf-8").read()
orig = html

def rep(old, new, must=True):
    global html
    if old not in html:
        if must:
            raise SystemExit("NOT FOUND: " + old[:80])
        return False
    assert html.count(old) == 1, "AMBIGUOUS: " + old[:80]
    html = html.replace(old, new, 1)
    return True

# ---------- 1. FAQPage JSON-LD in <head> (must match new visible FAQ below) ----------
faq_ld_old_start = "  <!-- Structured Data: FAQ -->"
faq_ld_old_end = "</script>"
i0 = html.find(faq_ld_old_start)
i1 = html.find(faq_ld_old_end, i0) + len(faq_ld_old_end)
faq_ld_old = html[i0:i1]

faq_ld_new = """  <!-- Structured Data: FAQ -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is an AI legal assistant?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "An AI legal assistant is legal AI software that helps law firms ask legal questions, research legal topics, review and analyze contracts and documents, and create legal drafts, with source citations on every output and attorney review before anything is used."
        }
      },
      {
        "@type": "Question",
        "name": "Is LexiFlow an AI lawyer that gives legal advice?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "No. LexiFlow is an AI legal assistant for lawyers and law firms. It supports research, contract review, document analysis, and drafting, but it does not give legal advice and does not replace a licensed attorney. Every output is reviewed by your team before use."
        }
      },
      {
        "@type": "Question",
        "name": "What can LexiFlow do with contracts?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "LexiFlow provides AI contract review and AI contract analysis: it flags risky clauses, missing terms, and deadlines, and links every finding to the exact clause text so your team can verify it before acting."
        }
      },
      {
        "@type": "Question",
        "name": "How does LexiFlow keep legal work accurate?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Accuracy first. Every AI output carries a citation back to its source, severity and confidence levels on findings, and a full audit trail. Attorneys remain in the loop on every decision before anything leaves the firm."
        }
      },
      {
        "@type": "Question",
        "name": "Is LexiFlow HIPAA compliant?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Yes. We sign BAAs with firms handling PHI, maintain SOC 2 alignment, and provide attorney-in-the-loop controls aligned with state bar ethics guidelines."
        }
      },
      {
        "@type": "Question",
        "name": "Which CRMs integrate with LexiFlow?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Native API integrations with Clio Grow, Clio Manage, Filevine, and MyCase. Sync is bidirectional: CRM updates flow back to your LexiFlow workspace."
        }
      }
    ]
  }
  </script>"""

html = html[:i0] + faq_ld_new + html[i1:]

# ---------- 2. Replace demo/case-study body block (Hero A through FAQ section) ----------
block_start = "<!-- Hero A: Workspace Copy -->"
block_end = "<!-- Ethics & Footer -->"
b0 = html.find(block_start)
b1 = html.find(block_end)
assert b0 != -1 and b1 != -1, "body anchors missing"
assert b0 < b1

new_body = """<!-- Hero A: AI Legal Assistant -->
<header class="hero">
  <div class="hero-container">
    <div>
      <div style="display:inline-block;padding:8px 16px;background:rgba(201,168,76,0.1);color:var(--gold);border-radius:100px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:24px;">&#x26a1; Your Live Workspace Demo Is Ready</div>
      <h1>Your AI Legal Assistant &mdash; <span>Ask, Research, Review &amp; Draft</span></h1>
      <p>This is what an AI legal assistant does in practice. LexiFlow is legal AI software for law firms: ask legal questions, research legal topics, review and analyze contracts, and create legal drafts &mdash; all in one workspace. Every answer is cited to its source, and every output is reviewed by an attorney before it leaves your firm.</p>
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <a href="/signup" class="btn-cta" style="font-size:16px;padding:16px 32px;"><i class="bi bi-rocket-takeoff"></i> Start Free Trial &rarr;</a>
        <a href="#guided-tour" class="btn-outline-light" style="font-size:16px;padding:16px 32px;"><i class="bi bi-play-circle"></i> Take the Guided Tour &rarr;</a>
      </div>
    </div>
    <!-- Hero B: Workspace Capabilities -->
    <div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.1);border-radius:32px;padding:40px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:24px;">
          <span style="width:10px;height:10px;background:#22c55e;border-radius:50%;display:inline-block;animation:pulse 2s infinite;"></span>
          <span style="font-family:var(--font-serif);font-size:20px;color:var(--gold);">Your AI Legal Assistant</span>
          <span style="background:rgba(201,168,76,0.15);color:var(--gold);padding:2px 10px;border-radius:100px;font-size:11px;font-weight:600;">LIVE</span>
        </div>
        <div style="border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:20px;margin-bottom:20px;">
          <div style="font-size:14px;font-weight:600;color:white;margin-bottom:4px;">One Workspace &middot; Every Legal AI Tool</div>
          <div style="font-size:12px;color:var(--slate-400);">Legal research, contract review, document analysis &amp; drafting</div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
          <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px;"><div style="font-size:11px;color:var(--slate-400);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">AI Legal Research</div><div style="font-size:13px;color:rgba(255,255,255,0.85);">Cited answers to legal questions</div></div>
          <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px;"><div style="font-size:11px;color:var(--slate-400);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">AI Contract Review</div><div style="font-size:13px;color:rgba(255,255,255,0.85);">Risk flags with clause citations</div></div>
          <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px;"><div style="font-size:11px;color:var(--slate-400);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">AI Legal Document Analysis</div><div style="font-size:13px;color:rgba(255,255,255,0.85);">Facts and issues, source-cited</div></div>
          <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px;"><div style="font-size:11px;color:var(--slate-400);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">AI Legal Drafting</div><div style="font-size:13px;color:rgba(255,255,255,0.85);">Case-aware first drafts</div></div>
        </div>
        <a href="/dashboard" style="display:block;margin-top:24px;font-size:13px;color:var(--gold);text-decoration:none;">Open the workspace dashboard &rarr;</a>
        <img src="/assets/screenshots/dashboard-hero.svg" alt="AI Legal Assistant dashboard for law firm case management" style="width:100%;margin-top:24px;border-radius:12px;border:1px solid rgba(255,255,255,0.12);" loading="lazy" />
      </div>
    </div>
  </div>
</header>

<!-- Capability Cards -->
<main>
  <section class="grid" id="guided-tour">
    <h2 style="font-family:var(--font-serif);font-size:28px;font-weight:800;text-align:center;color:var(--navy);margin-bottom:16px;grid-column:1/-1;">What Your AI Legal Assistant Automates</h2>
    <p style="color:var(--slate-600);font-size:16px;text-align:center;max-width:650px;margin:0 auto 32px;grid-column:1/-1;">AI tools for lawyers that turn questions into cited answers and drafts &mdash; with your team in control of every decision.</p>
    <div class="card"><i class="bi bi-search"></i><h3>AI Legal Research</h3><p>Ask a legal question in plain language and get jurisdiction-aware answers with citations. Verify every proposition against the source before it reaches a memo.</p></div>
    <div class="card"><i class="bi bi-file-earmark-text"></i><h3>AI Contract Review</h3><p>Upload an agreement and flag risky clauses, missing terms, and deadlines. Every flag links back to the exact clause text so your team can confirm it.</p></div>
    <div class="card"><i class="bi bi-diagram-3"></i><h3>AI Contract Analysis</h3><p>Compare contract language against your firm's playbooks and surface deviations, one-sided terms, and renewal or termination traps before they cost you.</p></div>
    <div class="card"><i class="bi bi-folder2-open"></i><h3>AI Legal Document Review</h3><p>Move through discovery and records faster with entity extraction, issue flags, and source citations on every finding your team wants to rely on.</p></div>
    <div class="card"><i class="bi bi-file-earmark-ruled"></i><h3>AI Legal Document Analysis</h3><p>Turn deposition transcripts and medical records into structured intelligence: chronologies, key admissions, and contradictions &mdash; each one cited to its source.</p></div>
    <div class="card"><i class="bi bi-pencil-square"></i><h3>AI Legal Drafting</h3><p>Generate demand letters, chronologies, and internal memos pre-populated with your case facts. Every statement carries a citation for final attorney review.</p></div>
    <div class="card"><i class="bi bi-headset"></i><h3>AI Legal Help &amp; Intake</h3><p>Never miss a lead. AI intake answers calls and web forms around the clock, qualifies potential clients, and syncs the results to your CRM.</p></div>
    <div class="card"><i class="bi bi-shield-lock"></i><h3>Legal AI Software You Can Trust</h3><p>HIPAA-grade data handling, signed BAAs, SOC 2 alignment, and a full audit trail on every AI action. Accuracy first, defensible by design.</p></div>
    <div class="card"><i class="bi bi-person-badge"></i><h3>AI Legal Assistant for Lawyers</h3><p>Attorney-in-the-loop on every decision. LexiFlow supports your firm's research, review, and drafting &mdash; it never replaces a licensed lawyer or gives legal advice.</p></div>
  </section>

  <!-- How It Works -->
  <section style="background:var(--navy);color:white;padding:80px 0;overflow:hidden;">
    <div style="max-width:var(--max-width);margin:0 auto;padding:0 40px;">
      <div style="text-align:center;margin-bottom:48px;">
        <div style="display:inline-block;padding:8px 16px;background:rgba(201,168,76,0.1);color:var(--gold);border-radius:100px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;">&#x26a1; How It Works &middot; One Workspace, Every Legal Task</div>
        <h2 style="font-family:var(--font-serif);font-size:40px;font-weight:800;margin-bottom:8px;">From Legal Question to <span style="color:var(--gold);">Cited Draft</span></h2>
        <p style="color:var(--slate-400);font-size:18px;max-width:640px;margin:0 auto;">Your AI legal assistant follows the same accuracy-first workflow for research, contract review, document analysis, and drafting: ingest, analyze, cite, and put the attorney in the loop.</p>
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:48px;">
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;text-align:center;"><div style="font-family:var(--font-serif);font-size:24px;font-weight:800;color:var(--gold);margin-bottom:6px;">1. Ask</div><div style="font-size:12px;color:var(--slate-400);text-transform:uppercase;letter-spacing:0.05em;">Ask legal questions or upload documents</div></div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;text-align:center;"><div style="font-family:var(--font-serif);font-size:24px;font-weight:800;color:var(--gold);margin-bottom:6px;">2. Analyze</div><div style="font-size:12px;color:var(--slate-400);text-transform:uppercase;letter-spacing:0.05em;">Research, review, and extract with reasoning AI</div></div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;text-align:center;"><div style="font-family:var(--font-serif);font-size:24px;font-weight:800;color:var(--gold);margin-bottom:6px;">3. Cite</div><div style="font-size:12px;color:var(--slate-400);text-transform:uppercase;letter-spacing:0.05em;">Every finding linked to its source</div></div>
        <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:24px;text-align:center;"><div style="font-family:var(--font-serif);font-size:24px;font-weight:800;color:var(--gold);margin-bottom:6px;">4. Review</div><div style="font-size:12px;color:var(--slate-400);text-transform:uppercase;letter-spacing:0.05em;">Attorney signs off before anything leaves the firm</div></div>
      </div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.1);border-radius:24px;padding:40px;margin-bottom:40px;">
        <div style="font-size:12px;font-weight:600;color:var(--gold);text-transform:uppercase;letter-spacing:0.05em;margin-bottom:16px;">What Your Firm Can Do With It</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;">
          <div style="background:rgba(255,255,255,0.04);border-left:3px solid var(--gold);padding:16px;border-radius:8px;"><p style="font-size:14px;color:rgba(255,255,255,0.9);margin-bottom:6px;"><strong>AI contract review &amp; analysis</strong></p><p style="font-size:12px;color:var(--slate-400);">Flag risk language and missing terms in minutes &mdash; with the clause text on screen to confirm.</p></div>
          <div style="background:rgba(255,255,255,0.04);border-left:3px solid var(--gold);padding:16px;border-radius:8px;"><p style="font-size:14px;color:rgba(255,255,255,0.9);margin-bottom:6px;"><strong>AI legal research</strong></p><p style="font-size:12px;color:var(--slate-400);">Get cited summaries of statutes and case law before your team starts writing.</p></div>
          <div style="background:rgba(255,255,255,0.04);border-left:3px solid var(--gold);padding:16px;border-radius:8px;"><p style="font-size:14px;color:rgba(255,255,255,0.9);margin-bottom:6px;"><strong>AI legal document review &amp; analysis</strong></p><p style="font-size:12px;color:var(--slate-400);">Turn transcripts, records, and discovery into structured, source-cited intelligence.</p></div>
          <div style="background:rgba(255,255,255,0.04);border-left:3px solid var(--gold);padding:16px;border-radius:8px;"><p style="font-size:14px;color:rgba(255,255,255,0.9);margin-bottom:6px;"><strong>AI legal drafting</strong></p><p style="font-size:12px;color:var(--slate-400);">Generate case-aware first drafts that your attorneys refine, not start from scratch.</p></div>
        </div>
        <div style="text-align:center;margin-top:32px;">
          <a href="/signup" class="btn-cta" style="font-size:16px;padding:16px 32px;"><i class="bi bi-rocket-takeoff"></i> Start Free Trial &rarr;</a>
          <a href="/case-studies" class="btn-outline-light" style="font-size:16px;padding:16px 32px;margin-left:12px;"><i class="bi bi-folder2-open"></i> Explore Case Studies</a>
        </div>
      </div>
    </div>
  </section>

  <!-- FAQ -->
  <section style="background:#fff;padding:80px 0;max-width:var(--max-width);margin:0 auto;padding-left:40px;padding-right:40px;">
    <div style="text-align:center;margin-bottom:50px;">
      <span style="display:inline-block;padding:8px;background:rgba(201,168,76,0.1);color:var(--gold);border-radius:4px;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:16px;">Common Questions</span>
      <h2 style="font-family:var(--font-serif);font-size:36px;color:var(--navy);margin-bottom:16px;">AI Legal Assistant FAQs</h2>
      <p style="color:var(--slate-600);font-size:16px;max-width:600px;margin:0 auto;">Straight answers about what the AI legal assistant can and can't do for your firm.</p>
    </div>
    <div style="display:flex;flex-direction:column;gap:24px;max-width:800px;margin:0 auto;">
      <div style="background:var(--slate-50);padding:32px;border-radius:16px;border:1px solid var(--slate-200);"><h4 style="font-family:var(--font-serif);font-size:20px;color:var(--navy);margin-bottom:12px;">What is an AI legal assistant?</h4><p style="color:var(--slate-600);font-size:15px;">An AI legal assistant is legal AI software that helps law firms ask legal questions, research legal topics, review and analyze contracts and documents, and create legal drafts &mdash; with source citations on every output and attorney review before anything is used.</p></div>
      <div style="background:var(--slate-50);padding:32px;border-radius:16px;border:1px solid var(--slate-200);"><h4 style="font-family:var(--font-serif);font-size:20px;color:var(--navy);margin-bottom:12px;">Is LexiFlow an AI lawyer that gives legal advice?</h4><p style="color:var(--slate-600);font-size:15px;">No. LexiFlow is an AI legal assistant for lawyers and law firms. It supports research, contract review, document analysis, and drafting, but it does not give legal advice and does not replace a licensed attorney. Every output is reviewed by your team before use.</p></div>
      <div style="background:var(--slate-50);padding:32px;border-radius:16px;border:1px solid var(--slate-200);"><h4 style="font-family:var(--font-serif);font-size:20px;color:var(--navy);margin-bottom:12px;">What can LexiFlow do with contracts?</h4><p style="color:var(--slate-600);font-size:15px;">LexiFlow provides AI contract review and AI contract analysis: it flags risky clauses, missing terms, and deadlines, and links every finding to the exact clause text so your team can verify it before acting.</p></div>
      <div style="background:var(--slate-50);padding:32px;border-radius:16px;border:1px solid var(--slate-200);"><h4 style="font-family:var(--font-serif);font-size:20px;color:var(--navy);margin-bottom:12px;">How does LexiFlow keep legal work accurate?</h4><p style="color:var(--slate-600);font-size:15px;">Accuracy first. Every AI output carries a citation back to its source, severity and confidence levels on findings, and a full audit trail. Attorneys remain in the loop on every decision before anything leaves the firm.</p></div>
      <div style="background:var(--slate-50);padding:32px;border-radius:16px;border:1px solid var(--slate-200);"><h4 style="font-family:var(--font-serif);font-size:20px;color:var(--navy);margin-bottom:12px;">Is LexiFlow HIPAA compliant?</h4><p style="color:var(--slate-600);font-size:15px;">Yes. We sign BAAs with firms handling PHI, maintain SOC 2 alignment, and provide attorney-in-the-loop controls aligned with state bar ethics guidelines.</p></div>
      <div style="background:var(--slate-50);padding:32px;border-radius:16px;border:1px solid var(--slate-200);"><h4 style="font-family:var(--font-serif);font-size:20px;color:var(--navy);margin-bottom:12px;">Which CRMs integrate with LexiFlow?</h4><p style="color:var(--slate-600);font-size:15px;">Native API integrations with Clio Grow, Clio Manage, Filevine, and MyCase. Sync is bidirectional: CRM updates flow back to your LexiFlow workspace.</p></div>
    </div>
  </section>

"""
html = html[:b0] + new_body + html[b1:]

io.open(path, "w", encoding="utf-8").write(html)
print("OK - homepage copy revised")

# ---------- Validation ----------
html = io.open(path, encoding="utf-8").read()
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
for b in blocks:
    json.loads(b)
print("JSON-LD valid:", [json.loads(b).get("@type") for b in blocks])
print("FAQ schema count:", len(json.loads([b for b in blocks if '"FAQPage"' in b][0])["mainEntity"]))
h4s = re.findall(r'<h4[^>]*>(.*?)</h4>', html, re.S)
print("Visible FAQ h4 count:", len([h for h in h4s if '?' in h]))
print("H1 count:", len(re.findall(r'<h1', html)))
print("Rodriguez mentions:", html.count("Rodriguez"))
print("Mount Sinai mentions:", html.count("Mount Sinai"))
kw = ["AI legal assistant","AI lawyer","AI legal help","AI legal advice","AI legal research","AI contract review","AI contract analysis","AI legal document review","AI legal document analysis","AI legal drafting","legal AI software","AI tools for lawyers","AI legal assistant for lawyers"]
for k in kw:
    print(f"  '{k}': {html.count(k)}")
