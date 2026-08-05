#!/usr/bin/env python3
"""Generate 7 AI Legal Assistant supporting pages for LexiFlow with shared header/footer."""
import io, os, re

ROOT = "/home/agent-frontend-developer/lexflow-seo"

# --- Extract shared nav + footer from the standard template page ---
tpl_path = os.path.join(ROOT, "ai-legal-intake-software.html")
with io.open(tpl_path, encoding="utf-8") as f:
    tpl = f.read()

m_nav = re.search(r"<!-- Navigation -->\s*<nav>.*?</nav>", tpl, re.S)
m_footer = re.search(r"<!-- Footer -->\s*<footer>.*?</footer>", tpl, re.S)
assert m_nav and m_footer, "nav/footer not found in template"
NAV = m_nav.group(0)
FOOTER = m_footer.group(0)
print("nav chars:", len(NAV), "footer chars:", len(FOOTER))

# --- Shared style block (modeled on template page) ---
STYLE = """<style>
    :root { --primary:#1a3a5c; --accent:#c9a84c; --navy:#0f172a; --gold:#c9a84c; --text-muted:#6b7280; --border:#e2e8f0; --bg-light:#f8fafc; --radius:8px; --radius-lg:16px; --font-sans:'Inter',sans-serif; --font-serif:'Playfair Display',Georgia,serif; }
    * { box-sizing:border-box; margin:0; padding:0; }
    body { font-family:var(--font-sans); color:#1a1a2e; background:var(--bg-light); line-height:1.6; }
    .container { max-width:1100px; margin:0 auto; padding:0 24px; }
    .hero { padding:120px 0 50px; background:linear-gradient(135deg,#0d1f33,var(--primary),#2a5a8c); color:#fff; text-align:center; }
    .hero h1 { font-family:var(--font-serif); font-size:2.8rem; margin-bottom:16px; }
    .hero h1 span { color:var(--accent); }
    .hero p { color:rgba(255,255,255,0.85); max-width:650px; margin:0 auto 28px; }
    .btn { display:inline-flex; align-items:center; gap:8px; padding:14px 28px; border-radius:var(--radius); font-weight:700; text-decoration:none; cursor:pointer; border:none; }
    .btn-primary { background:var(--accent); color:#0d1f33; }
    .btn-outline-light { background:transparent; color:#fff; border:1px solid rgba(255,255,255,0.3); }
    .section { padding:60px 0; }
    .section-alt { background:#fff; }
    .section h2 { font-family:var(--font-serif); font-size:2rem; color:var(--navy); text-align:center; margin-bottom:12px; }
    .section-label { color:var(--gold); text-transform:uppercase; font-size:12px; font-weight:700; letter-spacing:0.1em; display:block; text-align:center; margin-bottom:8px; }
    .grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:24px; }
    .card { background:#fff; border:1px solid var(--border); border-radius:var(--radius-lg); padding:28px; }
    .card h3 { font-size:1rem; color:var(--navy); margin-bottom:6px; }
    .card p { font-size:0.85rem; color:var(--text-muted); }
    .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; max-width:800px; margin:30px auto; }
    .stat { background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); border-radius:var(--radius); padding:16px; }
    .stat .num { font-family:var(--font-serif); font-size:1.8rem; font-weight:800; color:var(--accent); }
    .stat .label { font-size:0.72rem; color:rgba(255,255,255,0.7); text-transform:uppercase; }
    .two-col { display:grid; grid-template-columns:1fr 1fr; gap:40px; align-items:start; }
    .info-card { background:#fff; border:1px solid var(--border); border-radius:var(--radius-lg); padding:32px; }
    .info-card h3 { font-family:var(--font-serif); font-size:1.3rem; color:var(--navy); margin-bottom:12px; display:flex; align-items:center; gap:10px; }
    .info-card ul { list-style:none; padding:0; }
    .info-card ul li { padding:8px 0; border-bottom:1px solid var(--border); font-size:14px; color:var(--text-muted); display:flex; align-items:center; gap:10px; }
    .info-card ul li:last-child { border-bottom:none; }
    .info-card ul li i { color:var(--gold); }
    .badge-accuracy { display:inline-flex; align-items:center; gap:6px; background:rgba(34,197,94,0.15); color:#4ade80; border:1px solid rgba(34,197,94,0.3); padding:6px 14px; border-radius:100px; font-weight:600; font-size:13px; text-transform:uppercase; letter-spacing:0.05em; }
    @media (max-width:900px) { .grid-3 { grid-template-columns:1fr; } .stats { grid-template-columns:repeat(2,1fr); } .two-col { grid-template-columns:1fr; } }
    @media (max-width:768px) { .hero h1 { font-size:1.4rem; } }
  </style>"""

# --- Page definitions: slug, title, description, keywords, canonical, H1, hero p, sections ---
PAGES = [
    {
        "slug": "ai-contract-review",
        "title": "AI Contract Review — Find Risks Faster | LexiFlow",
        "description": "AI contract review for law firms: flag risky clauses, missing terms, and deadlines in minutes. Traceable, defensible analysis your team can rely on.",
        "keywords": "AI contract review, contract analysis software, contract clause detection, legal document review AI, contract risk flags",
        "h1": "AI Contract Review <span>for Law Firms</span>",
        "badge": "Reasoning AI — Not a Keyword Search",
        "hero_p": "Reviewing a 40-page agreement line by line is slow, expensive, and error-prone. LexiFlow's AI contract review reads every clause, flags risk language, surfaces missing terms, and gives your team a source-cited map of what changed or what is missing — in minutes, not days.",
        "body": """
<!-- What It Does -->
<section class="section section-alt"><div class="container">
  <span class="section-label">What It Does</span>
  <h2>Clause-Level Review With Source Citations</h2>
  <p style="text-align:center;color:var(--text-muted);max-width:720px;margin:0 auto 32px;">LexiFlow parses the agreement into clauses, compares them against your firm's playbooks and common risk patterns, and produces a review memo where every flag links back to the exact clause text.</p>
  <div class="grid-3">
    <div class="card"><h3>🔍 Risk Flags</h3><p>Indemnity, liability caps, auto-renewal, exclusivity, non-compete, and change-of-control language flagged with severity levels and plain-English explanations.</p></div>
    <div class="card"><h3>📋 Missing Terms</h3><p>Detects absent boilerplate your playbook requires: governing law, dispute resolution, notice periods, assignment rights, and data protection terms.</p></div>
    <div class="card"><h3>⏱️ Deadline Extraction</h3><p>Auto-extracts renewal windows, termination notices, and performance deadlines into a timeline your team can calendar from day one.</p></div>
  </div>
</div></section>
<!-- Why It Matters -->
<section class="section"><div class="container">
  <span class="section-label">Why It Matters</span>
  <h2>Accuracy You Can Defend</h2>
  <div class="two-col">
    <div class="info-card"><h3><i class="bi bi-shield-check"></i> Every Flag Is Traceable</h3><ul>
      <li><i class="bi bi-check2"></i> Citation back to clause, paragraph, and line</li>
      <li><i class="bi bi-check2"></i> Severity classification: Critical / Significant / Minor</li>
      <li><i class="bi bi-check2"></i> Plain-English rationale written for client review</li>
      <li><i class="bi bi-check2"></i> Exportable redline-ready summary memo</li>
    </ul></div>
    <div class="info-card"><h3><i class="bi bi-robot"></i> Built for Attorney Review</h3><ul>
      <li><i class="bi bi-check2"></i> Attorneys stay in the loop on every recommendation</li>
      <li><i class="bi bi-check2"></i> No legal advice generated without human sign-off</li>
      <li><i class="bi bi-check2"></i> HIPAA-grade data handling and signed BAAs available</li>
      <li><i class="bi bi-check2"></i> Works alongside your existing document systems</li>
    </ul></div>
  </div>
</div></section>
""",
    },
    {
        "slug": "ai-legal-research",
        "title": "AI Legal Research — Faster, Cited Answers | LexiFlow",
        "description": "AI legal research that summarizes statutes and case law with citations. Ask in plain language, get jurisdiction-aware answers your team can verify.",
        "keywords": "AI legal research, legal research assistant, case law summary AI, statute research tool, law firm research automation",
        "h1": "AI Legal Research <span>for Modern Law Firms</span>",
        "badge": "Reasoning AI — Cited, Not Guessed",
        "hero_p": "Legal research should not be a weekend-long hunt. LexiFlow's AI legal research assistant takes plain-language questions, returns jurisdiction-aware answers, and attaches citations to every proposition so your team can verify the law before it ever reaches a filing.",
        "body": """
<!-- How It Works -->
<section class="section section-alt"><div class="container">
  <span class="section-label">How It Works</span>
  <h2>From Question to Cited Answer</h2>
  <p style="text-align:center;color:var(--text-muted);max-width:720px;margin:0 auto 32px;">Ask a research question the way you would ask a colleague. LexiFlow surfaces relevant statutes, cases, and secondary authority — then shows its work.</p>
  <div class="grid-3">
    <div class="card"><h3>💬 Plain-Language Queries</h3><p>No boolean syntax required. Ask about a doctrine, a deadline, or an element and get a structured answer with authority lists.</p></div>
    <div class="card"><h3>📍 Jurisdiction Awareness</h3><p>Answers are scoped to the jurisdictions you specify, with citations that respect state and federal hierarchy.</p></div>
    <div class="card"><h3>🔗 Verifiable Citations</h3><p>Every proposition links to the underlying source so a researcher can confirm the law before it reaches a memo.</p></div>
  </div>
</div></section>
<!-- Research workflow -->
<section class="section"><div class="container">
  <span class="section-label">Workflow</span>
  <h2>Built Into Your Research Pipeline</h2>
  <div class="two-col">
    <div class="info-card"><h3><i class="bi bi-clock-history"></i> Faster First Draft</h3><ul>
      <li><i class="bi bi-check2"></i> Research memos drafted with cited authority</li>
      <li><i class="bi bi-check2"></i> Statute-of-limitations lookups in seconds</li>
      <li><i class="bi bi-check2"></i> Case-law summaries with holding and reasoning</li>
      <li><i class="bi bi-check2"></i> Spot-check gaps before you start writing</li>
    </ul></div>
    <div class="info-card"><h3><i class="bi bi-person-check"></i> Attorney-Verified Output</h3><ul>
      <li><i class="bi bi-check2"></i> Every citation reviewed before use</li>
      <li><i class="bi bi-check2"></i> Confidence levels on ambiguous authority</li>
      <li><i class="bi bi-check2"></i> Audit trail of sources consulted</li>
      <li><i class="bi bi-check2"></i> Accuracy-first defaults you can trust</li>
    </ul></div>
  </div>
</div></section>
""",
    },
    {
        "slug": "ai-legal-document-analysis",
        "title": "AI Legal Document Analysis — Source-Cited Insights | LexiFlow",
        "description": "AI legal document analysis for discovery, records, and contracts: extract facts, flag issues, and link every finding to its source document.",
        "keywords": "AI legal document analysis, document review AI, legal document insights, discovery document analysis, record review software",
        "h1": "AI Legal Document Analysis <span>That Shows Its Work</span>",
        "badge": "Accuracy First — Every Finding Cited",
        "hero_p": "Whether it is a deposition transcript, a medical record, or a contract, the value of analysis is only as good as its source. LexiFlow's AI legal document analysis extracts facts and flags issues, then links every finding back to the exact page, line, or clause it came from.",
        "body": """
<!-- What You Get -->
<section class="section section-alt"><div class="container">
  <span class="section-label">What You Get</span>
  <h2>Structured Intelligence From Unstructured Files</h2>
  <p style="text-align:center;color:var(--text-muted);max-width:720px;margin:0 auto 32px;">Upload documents in bulk and let LexiFlow build a searchable, tagged, source-cited analysis layer on top of your existing records.</p>
  <div class="grid-3">
    <div class="card"><h3>🗂️ Entity &amp; Fact Extraction</h3><p>Parties, dates, amounts, and key events extracted into structured fields you can filter, sort, and export.</p></div>
    <div class="card"><h3>🚩 Issue Spotting</h3><p>Contradictions, gaps, and risk language flagged with severity and a plain-English explanation of why it matters.</p></div>
    <div class="card"><h3>📎 Source Citations</h3><p>Every extracted fact links back to its source so anyone on the team can verify the finding in seconds.</p></div>
  </div>
</div></section>
<!-- Where it fits -->
<section class="section"><div class="container">
  <span class="section-label">Where It Fits</span>
  <h2>One Analysis Layer, Every Workflow</h2>
  <div class="two-col">
    <div class="info-card"><h3><i class="bi bi-journal-text"></i> Discovery &amp; Depositions</h3><ul>
      <li><i class="bi bi-check2"></i> Contradiction detection across transcripts and records</li>
      <li><i class="bi bi-check2"></i> Chronology and timeline generation</li>
      <li><i class="bi bi-check2"></i> Key admission extraction with citations</li>
      <li><i class="bi bi-check2"></i> Cross-examination question drafting support</li>
    </ul></div>
    <div class="info-card"><h3><i class="bi bi-file-earmark-text"></i> Contracts &amp; Records</h3><ul>
      <li><i class="bi bi-check2"></i> Contract clause and obligation extraction</li>
      <li><i class="bi bi-check2"></i> Medical record chronology and gap flags</li>
      <li><i class="bi bi-check2"></i> Privilege and relevance tagging support</li>
      <li><i class="bi bi-check2"></i> Export-ready reports for your team</li>
    </ul></div>
  </div>
</div></section>
""",
    },
    {
        "slug": "ai-legal-document-generator",
        "title": "AI Legal Document Generator — Draft Faster | LexiFlow",
        "description": "AI legal document generator for demand letters, chronologies, and drafts — pre-populated with case facts and source citations your team can refine.",
        "keywords": "AI legal document generator, legal document drafting AI, demand letter generator, legal drafting software, law firm document automation",
        "h1": "AI Legal Document Generator <span>for Plaintiff Firms</span>",
        "badge": "Draft With Context — Not Blank Templates",
        "hero_p": "The fastest way to a great draft is a draft that already knows your case. LexiFlow's AI legal document generator pre-populates demand letters, chronologies, and internal memos with your case facts and source citations — so your team edits substance, not scaffolding.",
        "body": """
<!-- What You Can Generate -->
<section class="section section-alt"><div class="container">
  <span class="section-label">What You Can Generate</span>
  <h2>Case-Aware Drafts in Minutes</h2>
  <p style="text-align:center;color:var(--text-muted);max-width:720px;margin:0 auto 32px;">Every document is grounded in the facts LexiFlow already extracted from your intake, records, and discovery — and every statement carries a citation back to its source.</p>
  <div class="grid-3">
    <div class="card"><h3>📨 Demand Letters</h3><p>Pre-populated with case facts, chronology, and liability analysis. Every assertion links to the supporting record.</p></div>
    <div class="card"><h3>📅 Chronologies</h3><p>Auto-built medical and fact timelines with source references on each entry, ready for your review.</p></div>
    <div class="card"><h3>📝 Internal Memos</h3><p>Merit assessments, research memos, and case summaries drafted from your workspace data.</p></div>
  </div>
</div></section>
<!-- How it stays accurate -->
<section class="section"><div class="container">
  <span class="section-label">Accuracy First</span>
  <h2>Built for Attorney Review</h2>
  <div class="two-col">
    <div class="info-card"><h3><i class="bi bi-pencil-square"></i> Edit, Don't Start Over</h3><ul>
      <li><i class="bi bi-check2"></i> Drafts pre-populated from your actual case data</li>
      <li><i class="bi bi-check2"></i> Source citations on every factual statement</li>
      <li><i class="bi bi-check2"></i> Jurisdiction-aware defaults where relevant</li>
      <li><i class="bi bi-check2"></i> Export to Word or PDF for final review</li>
    </ul></div>
    <div class="info-card"><h3><i class="bi bi-shield-lock"></i> Defensible Output</h3><ul>
      <li><i class="bi bi-check2"></i> Every draft tracked with an audit trail</li>
      <li><i class="bi bi-check2"></i> No draft leaves your firm without attorney sign-off</li>
      <li><i class="bi bi-check2"></i> HIPAA-grade handling for medical records</li>
      <li><i class="bi bi-check2"></i> Works with Clio, Filevine, and MyCase data</li>
    </ul></div>
  </div>
</div></section>
""",
    },
    {
        "slug": "ai-legal-assistant-for-lawyers",
        "title": "AI Legal Assistant for Lawyers — Work Smarter | LexiFlow",
        "description": "The AI legal assistant for lawyers: automate intake, medical review, research, and drafting inside one workspace. Accuracy-first, attorney-in-the-loop.",
        "keywords": "AI legal assistant for lawyers, AI assistant for law firms, legal AI workspace, lawyer productivity AI, legal ops automation",
        "h1": "AI Legal Assistant <span>for Lawyers</span>",
        "badge": "One Workspace. Every AI Tool.",
        "hero_p": "LexiFlow is the AI legal assistant built for practicing lawyers: it qualifies intake, reviews medical records, analyzes depositions, runs legal research, and drafts documents — all inside one dashboard, all with citations, and all reviewed by an attorney before anything leaves the firm.",
        "body": """
<!-- The Workspace -->
<section class="section section-alt"><div class="container">
  <span class="section-label">The Workspace</span>
  <h2>Your Entire Practice, One Dashboard</h2>
  <p style="text-align:center;color:var(--text-muted);max-width:720px;margin:0 auto 32px;">Sign in to a unified workspace where the tools work from the same case data — no re-typing, no silos, no context switching.</p>
  <div class="grid-3">
    <div class="card"><h3>📥 AI Intake</h3><p>Conversational intake that qualifies leads, scores merits, and syncs to your CRM — 24/7, in multiple languages.</p></div>
    <div class="card"><h3>🩺 AI Medical</h3><p>Medical chronologies and merit review that surface treatment gaps and document the story of the case.</p></div>
    <div class="card"><h3>🎥 Veritas Deposition</h3><p>Deposition intelligence: contradictions, key admissions, and cross-examination support with source citations.</p></div>
    <div class="card"><h3>🗃️ Discovery Vault</h3><p>Index, de-duplicate, and tag discovery documents at scale — then find exactly what you need in seconds.</p></div>
    <div class="card"><h3>📈 Settlement Predictor</h3><p>Jurisdiction-aware settlement modeling that shows how venue and damages caps change case value.</p></div>
    <div class="card"><h3>🧭 Strategist</h3><p>Life care plans, opposing counsel profiles, statute-of-limitations tracking, and trial readiness scoring.</p></div>
  </div>
</div></section>
<!-- Why lawyers trust it -->
<section class="section"><div class="container">
  <span class="section-label">Why Lawyers Trust It</span>
  <h2>Accuracy First. Attorney in the Loop.</h2>
  <div class="two-col">
    <div class="info-card"><h3><i class="bi bi-check-circle"></i> Traceable by Design</h3><ul>
      <li><i class="bi bi-check2"></i> Every AI output cites its source</li>
      <li><i class="bi bi-check2"></i> Severity and confidence levels on findings</li>
      <li><i class="bi bi-check2"></i> Full audit trail of AI actions</li>
      <li><i class="bi bi-check2"></i> No output used without attorney review</li>
    </ul></div>
    <div class="info-card"><h3><i class="bi bi-speedometer2"></i> Built for Firms</h3><ul>
      <li><i class="bi bi-check2"></i> Clio, Filevine, and MyCase integrations</li>
      <li><i class="bi bi-check2"></i> HIPAA BAAs and SOC 2 alignment</li>
      <li><i class="bi bi-check2"></i> Scales from solo to high-volume firms</li>
      <li><i class="bi bi-check2"></i> 30-day free trial on every plan</li>
    </ul></div>
  </div>
</div></section>
""",
    },
    {
        "slug": "ai-legal-help",
        "title": "AI Legal Help — 24/7 Assistance for Your Firm | LexiFlow",
        "description": "AI legal help for law firms: 24/7 intake coverage, instant answers to routine questions, and AI assistance your whole team can rely on.",
        "keywords": "AI legal help, AI legal assistant help, 24/7 legal intake, legal AI assistance, law firm AI help",
        "h1": "AI Legal Help <span>for Your Whole Firm</span>",
        "badge": "24/7 Capacity. Human Oversight.",
        "hero_p": "When a potential client calls at 9 PM, your firm can still answer. LexiFlow's AI legal help covers intake around the clock, answers routine questions instantly, and routes complex matters to your attorneys — so no lead is missed and no attorney's time is wasted.",
        "body": """
<!-- Coverage -->
<section class="section section-alt"><div class="container">
  <span class="section-label">Coverage</span>
  <h2>Never Miss a Lead Again</h2>
  <p style="text-align:center;color:var(--text-muted);max-width:720px;margin:0 auto 32px;">Your clients reach out when they need help — not when your office is open. LexiFlow makes sure someone (or something) is always there to help.</p>
  <div class="grid-3">
    <div class="card"><h3>🌙 24/7 Intake</h3><p>Answer calls and web forms at any hour, in English or Spanish, and capture the full story before a lead goes cold.</p></div>
    <div class="card"><h3>❓ Instant Answers</h3><p>Handle routine questions about process, documents, and next steps — with escalation to an attorney when needed.</p></div>
    <div class="card"><h3>📲 Follow-Up That Converts</h3><p>Automated, on-brand follow-up that keeps leads warm until your team is ready to talk.</p></div>
  </div>
</div></section>
<!-- How help works -->
<section class="section"><div class="container">
  <span class="section-label">How It Works</span>
  <h2>Help That Scales With Your Firm</h2>
  <div class="two-col">
    <div class="info-card"><h3><i class="bi bi-headset"></i> For Clients</h3><ul>
      <li><i class="bi bi-check2"></i> Fast, friendly intake at any hour</li>
      <li><i class="bi bi-check2"></i> Clear next steps without jargon</li>
      <li><i class="bi bi-check2"></i> Spanish-language support included</li>
      <li><i class="bi bi-check2"></i> Human hand-off for complex matters</li>
    </ul></div>
    <div class="info-card"><h3><i class="bi bi-briefcase"></i> For Your Team</h3><ul>
      <li><i class="bi bi-check2"></i> Qualified leads, not raw calls</li>
      <li><i class="bi bi-check2"></i> Full transcripts and merit scores</li>
      <li><i class="bi bi-check2"></i> CRM sync in one click</li>
      <li><i class="bi bi-check2"></i> Attorney-in-the-loop on every decision</li>
    </ul></div>
  </div>
</div></section>
""",
    },
    {
        "slug": "ai-lawyer",
        "title": "AI Lawyer Assistant — What AI Can and Can't Do | LexiFlow",
        "description": "What an AI lawyer assistant can and can't do — and how LexiFlow keeps attorneys in the loop with traceable, defensible AI for legal work.",
        "keywords": "AI lawyer, AI lawyer assistant, artificial intelligence lawyer, AI for law firms, AI legal assistant ethics",
        "h1": "The AI Lawyer Assistant <span>Your Firm Can Trust</span>",
        "badge": "Assistance — Not Replacement",
        "hero_p": "AI is not replacing lawyers. It is giving them back their time. LexiFlow is an AI lawyer assistant that handles the repetitive work — intake, review, research, drafting — while every judgment call stays with a licensed attorney, backed by citations and an audit trail.",
        "body": """
<!-- What AI does -->
<section class="section section-alt"><div class="container">
  <span class="section-label">What AI Does</span>
  <h2>The Work AI Should Take Off Your Plate</h2>
  <p style="text-align:center;color:var(--text-muted);max-width:720px;margin:0 auto 32px;">LexiFlow focuses AI on the tasks that are repetitive, time-consuming, and fact-heavy — where consistency and speed matter most.</p>
  <div class="grid-3">
    <div class="card"><h3>📥 Intake &amp; Triage</h3><p>Capture complete client narratives, qualify leads, and score merits before an attorney ever picks up the phone.</p></div>
    <div class="card"><h3>🔎 Review &amp; Research</h3><p>Flag contract risks, summarize case law, and surface contradictions — each finding cited to its source.</p></div>
    <div class="card"><h3>📝 Drafting Support</h3><p>Generate first drafts of letters, chronologies, and memos from case facts your team can verify.</p></div>
  </div>
</div></section>
<!-- Ethics -->
<section class="section"><div class="container">
  <span class="section-label">Ethics &amp; Reality</span>
  <h2>What an AI Lawyer Assistant Can't Do</h2>
  <div class="two-col">
    <div class="info-card"><h3><i class="bi bi-person-badge"></i> Judgment Stays With You</h3><ul>
      <li><i class="bi bi-check2"></i> AI does not give legal advice</li>
      <li><i class="bi bi-check2"></i> AI does not appear in court</li>
      <li><i class="bi bi-check2"></i> Every output needs attorney review</li>
      <li><i class="bi bi-check2"></i> State bar ethics rules remain your guide</li>
    </ul></div>
    <div class="info-card"><h3><i class="bi bi-robot"></i> What It Does Better</h3><ul>
      <li><i class="bi bi-check2"></i> Reads thousands of pages consistently</li>
      <li><i class="bi bi-check2"></i> Never misses a 9 PM intake call</li>
      <li><i class="bi bi-check2"></i> Cites every fact to a source</li>
      <li><i class="bi bi-check2"></i> Keeps a complete audit trail</li>
    </ul></div>
  </div>
</div></section>
""",
    },
]

# --- Common head prefix/suffix ---
HEAD_PRE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
"""
HEAD_MID = """  <link rel="canonical" href="https://lexiflow.co/{slug}" />
  <!-- Open Graph / Social Sharing -->
  <meta property="og:title" content="{og_title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:url" content="https://lexiflow.co/{slug}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="LexiFlow Technologies Inc" />
  <meta property="og:image" content="https://lexiflow.co/social-banner.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:locale" content="en_US" />
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{og_title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="https://lexiflow.co/social-banner.png" />
  <!-- JSON-LD: Organization -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "LexiFlow Technologies Inc",
    "url": "https://lexiflow.co/",
    "logo": "https://lexiflow.co/branding/logo-icon.svg",
    "description": "{jsonld_org}"
  }}
  </script>
  <!-- JSON-LD: SoftwareApplication -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "LexiFlow {app_name}",
    "operatingSystem": "Web",
    "applicationCategory": "Legal Software",
    "description": "{jsonld_app}",
    "url": "https://lexiflow.co/{slug}",
    "offers": {{
      "@type": "Offer",
      "price": "29.00",
      "priceCurrency": "USD",
      "description": "Starts at $29/month"
    }}
  }}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap" rel="stylesheet" media="print" onload="this.media='all'" />
  <noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap" rel="stylesheet" /></noscript>
  <link rel="preload" as="style" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" />
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" media="print" onload="this.media='all'" />
  <noscript><link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" /></noscript>
  <link rel="stylesheet" href="/master-layout.css">
  <link rel="stylesheet" href="/shared-layout.css">
  {style}
</head>
<body>
"""

CTA = """<!-- CTA -->
<section id="cta" style="background: var(--navy); color: white; padding: 60px 0;">
  <div class="container" style="max-width: 700px; margin: 0 auto; text-align: center;">
    <div style="display: inline-block; background: rgba(201,168,76,0.1); color: #c9a84c; padding: 4px 12px; border-radius: 100px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px;">🤖 LexiFlow AI Legal Assistant</div>
    <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 2rem; margin-bottom: 8px;">See It In Your Workspace</h2>
    <p style="color: rgba(255,255,255,0.7); font-size: 14px; margin-bottom: 28px; max-width: 500px; margin-left: auto; margin-right: auto;">Try every AI tool free for 30 days — no credit card required. Your dashboard is ready in minutes.</p>
    <div style="text-align:center;padding:20px 0;">
      <a href="/signup" class="btn btn-primary" style="text-decoration:none;display:inline-flex;align-items:center;justify-content:center;padding:16px 40px;">Start Free Trial →</a>
      <a href="/" class="btn btn-outline-light" style="text-decoration:none;display:inline-flex;align-items:center;justify-content:center;margin-left:12px;">Back to Home</a>
    </div>
    <p style="color: rgba(255,255,255,0.4); font-size: 12px; margin-top: 20px;">🔒 HIPAA Compliant · SOC 2 Certified · Signed BAA Available</p>
  </div>
</section>
"""

def related_links(slug):
    links = [
        ("/", "AI Legal Assistant — Home"),
        ("/ai-contract-review", "AI Contract Review"),
        ("/ai-legal-research", "AI Legal Research"),
        ("/ai-legal-document-analysis", "AI Legal Document Analysis"),
        ("/ai-legal-document-generator", "AI Legal Document Generator"),
        ("/ai-legal-assistant-for-lawyers", "AI Legal Assistant for Lawyers"),
        ("/ai-legal-help", "AI Legal Help"),
        ("/ai-lawyer", "AI Lawyer Assistant"),
        ("/pricing", "Pricing &amp; Plans"),
    ]
    items = "\n".join(f'    <a href="{u}" style="color: #0f172a; text-decoration: none; font-weight: 600;">{label} →</a>' for u, label in links if u != "/" + slug)
    return f"""<!-- Related Resources -->
<section class="max-w-screen" style="padding: 40px 0; border-top: 1px solid var(--border); max-width: 1200px; margin: 0 auto; padding-left: 40px; padding-right: 40px;">
  <h3 style="font-family: 'Playfair Display', serif; font-size: 24px; margin-bottom: 20px; color: #0f172a;">Related AI Legal Resources</h3>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
{items}
  </div>
</section>
"""

def hero_block(p):
    return f"""<!-- Hero -->
<section class="hero"><div class="container">
  <div style="margin-bottom:20px;"><span class="badge-accuracy"><i class="bi bi-cpu"></i> {p['badge']}</span></div>
  <h1>{p['h1']}</h1>
  <p>{p['hero_p']}</p>
  <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
    <a href="/signup" class="btn btn-primary" style="text-decoration:none;display:inline-flex;align-items:center;justify-content:center;">🚀 Start Free Trial →</a>
    <a href="/" class="btn btn-outline-light"><i class="bi bi-arrow-left"></i> Back to Home</a>
  </div>
</div></section>
"""

for p in PAGES:
    slug = p["slug"]
    og_title = p["title"].replace("&", "&amp;")
    app_name = p.get("app_name", "AI Legal Assistant")
    jsonld_org = p.get("jsonld_org", "AI-powered legal assistant software for law firms — contract review, legal research, and document analysis.")
    jsonld_app = p.get("jsonld_app", p["description"])
    head = (
        HEAD_PRE
        + f'  <title>{p["title"]}</title>\n'
        + f'  <meta name="description" content="{p["description"]}" />\n'
        + f'  <meta name="keywords" content="{p["keywords"]}" />\n'
        + HEAD_MID.format(slug=slug, og_title=og_title, description=p["description"],
                          jsonld_org=jsonld_org, jsonld_app=jsonld_app, app_name=app_name,
                          style=STYLE)
    )
    page = (
        head
        + NAV + "\n"
        + hero_block(p)
        + p["body"]
        + CTA
        + related_links(slug)
        + FOOTER + "\n"
        + '<script src="/shared-layout.js"></script>\n'
        + "</body>\n</html>\n"
    )
    out = os.path.join(ROOT, slug + ".html")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote", slug + ".html", len(page), "bytes")
