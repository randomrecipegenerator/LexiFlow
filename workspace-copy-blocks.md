# "Your Workspace" — Immersive Live Tour Text Blocks

> **Purpose:** Replace marketing "features and benefits" copy with first-person "your workspace" language. These text blocks transform the landing experience into a live guided tour where the user feels they are already logged into the LexiFlow dashboard managing the *Rodriguez v. Mount Sinai* demo case.
>
> **Target pages:** index.html hero + feature grid, core landing pages (AI Intake, Veritas, Strategist, Auto-Doc Drafter)
>
> **For:** Frontend Engineer — drop these text blocks into the respective page templates.

---

## A. Index Hero Section — Replace Lines 284-291

**Current copy:**
> "LexiFlow is the premier legal document automation software and in-house legal software solution for plaintiff-side practices. We automate legal operations and legal matter management with Reasoning AI, syncing clinical intelligence into Clio, Filevine, and MyCase."

**Replace with (immersive workspace):**

```html
<div style="display: inline-block; padding: 8px 16px; background: rgba(201, 168, 76, 0.1); color: var(--gold); border-radius: 100px; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 24px;">
  ⚡ Your Live Demo Is Ready
</div>
<h1>Your Workspace for <span>Rodriguez v. Mount Sinai</span>.</h1>
<p>You are logged into a live case. In your dashboard, you can see an AI-qualified medical malpractice lead with a <strong>92/100 Merit Score</strong>, <strong>7 flagged contradictions</strong> in the deposition testimony, and a <strong>$4.2M estimated trial value</strong> — all generated in the time it took to read this sentence.</p>
<div style="display: flex; gap: 16px; justify-content: inherit;">
  <a href="/dashboard" class="btn-cta">Open Your Dashboard</a>
  <a href="#guided-tour" class="btn-cta" style="background: white; color: var(--navy);">Take the Guided Tour →</a>
</div>
```

---

## B. Index Hero Visual Panel — Replace Lines 293-297

**Current copy:**
> "MeritScan Live — AI currently analyzing 4,281 medical records for firms across the US."

**Replace with (live case status):**

```html
<div class="hero-visual" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 32px; padding: 40px;">
  <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
    <span style="width: 10px; height: 10px; background: #22c55e; border-radius: 50%; display: inline-block; animation: pulse 2s infinite;"></span>
    <span style="font-family: 'Playfair Display', serif; font-size: 20px; color: var(--gold);">Your Active Case</span>
    <span style="background: rgba(201,168,76,0.15); color: var(--gold); padding: 2px 10px; border-radius: 100px; font-size: 11px; font-weight: 600;">LIVE</span>
  </div>
  <div style="border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 20px; margin-bottom: 20px;">
    <div style="font-size: 14px; font-weight: 600; color: white; margin-bottom: 4px;">Rodriguez v. Mount Sinai Hospital</div>
    <div style="font-size: 12px; color: var(--slate-400);">Medical Malpractice — Delayed Sepsis Diagnosis</div>
  </div>
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
    <div>
      <div style="font-size: 11px; color: var(--slate-400); text-transform: uppercase; letter-spacing: 0.05em;">AI Merit Score</div>
      <div style="font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 800; color: var(--gold);">92<span style="font-size: 14px; color: var(--slate-400);">/100</span></div>
    </div>
    <div>
      <div style="font-size: 11px; color: var(--slate-400); text-transform: uppercase; letter-spacing: 0.05em;">Trial Value (NY)</div>
      <div style="font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 800; color: var(--gold);">$4.2M</div>
    </div>
    <div>
      <div style="font-size: 11px; color: var(--slate-400); text-transform: uppercase; letter-spacing: 0.05em;">Contradictions Found</div>
      <div style="font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 800; color: #ef4444;">7</div>
    </div>
    <div>
      <div style="font-size: 11px; color: var(--slate-400); text-transform: uppercase; letter-spacing: 0.05em;">Treatment Gap</div>
      <div style="font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 800; color: #ef4444;">14h</div>
    </div>
  </div>
  <a href="/dashboard" style="display: block; margin-top: 24px; font-size: 13px; color: var(--gold); text-decoration: none;">Open full case dashboard →</a>
</div>
```

---

## C. Feature Cards — Replace Lines 302-348

**Current copy:** Third-person feature descriptions ("Deploy our advanced AI legal intake software...")

**Replace each card with (first-person workspace):**

### Card 1: AI Intake
```html
<div class="card">
  <i class="bi bi-robot"></i>
  <h3>Your AI Intake Workspace</h3>
  <p>In your dashboard, Elena Rodriguez's intake conversation is already transcribed, scored, and synced to your CRM. You can see the AI's 92/100 merit score, click to hear the original intake call, and approve the lead for Filevine in one click — without re-typing a single data field.</p>
</div>
```

### Card 2: Medical Chronologies
```html
<div class="card">
  <i class="bi bi-calendar-check"></i>
  <h3>Your Medical Timeline</h3>
  <p>Open the chronology tab and you will see Ms. Rodriguez's complete Mount Sinai treatment history organized by date. The AI has highlighted the 14-hour gap between ER triage and antibiotic administration in red — click any entry to jump to the source medical record page.</p>
</div>
```

### Card 3: Discovery-Vault™
```html
<div class="card">
  <i class="bi bi-database-lock"></i>
  <h3>Your Discovery Repository</h3>
  <p>In your Discovery-Vault, 847 documents from Mount Sinai's production are already indexed, de-duplicated, and tagged by issue. You can filter by "sepsis protocol compliance" and see exactly 6 responsive documents — the AI has already extracted the key clinical timelines from each one.</p>
</div>
```

### Card 4: Settlement-Predictor™
```html
<div class="card">
  <i class="bi bi-graph-up"></i>
  <h3>Your Settlement Model</h3>
  <p>Open Settlement-Predictor Pro and you will see Ms. Rodriguez's case valued at $4.2M for New York — where there is no cap on non-economic damages. Toggle the jurisdiction to California and watch the estimate adjust to $353,000 under MICRA. The model factors in venue history, judge assignment, and defendant profile automatically.</p>
</div>
```

### Card 5: Veritas Deposition™
```html
<div class="card">
  <i class="bi bi-camera-reels"></i>
  <h3>Your Deposition Analysis</h3>
  <p>In your Veritas workspace, Dr. Miller's deposition transcript is open. The AI has flagged 7 contradictions against the medical records — including his claim that antibiotics started at 19:45 when the MAR shows no administration until 10:15. Three cross-examination questions are pre-generated, ready for your trial notebook.</p>
</div>
```

### Card 6: Compliance-Shield™
```html
<div class="card">
  <i class="bi bi-shield-check"></i>
  <h3>Your Compliance Log</h3>
  <p>In your Compliance-Shield dashboard, every AI action taken on this case has an immutable audit trail. You can see that the AI intake transcript was HIPAA-encrypted in transit, the medical records were BAA-protected, and all data transfers to Filevine were logged with timestamps and actor identities.</p>
</div>
```

### Card 7: Legal Operations
```html
<div class="card">
  <i class="bi bi-gear-wide-connected"></i>
  <h3>Your Legal Operations Hub</h3>
  <p>In your operations dashboard, you can see the full case lifecycle at a glance: intake completed in 3 seconds (vs. 4 hours manual), medical review completed in 90 seconds (vs. 6 hours manual), deposition analysis completed in 2 minutes (vs. 8 hours manual). Your firm's effective capacity just increased by 300% without adding headcount.</p>
</div>
```

### Card 8: Document Automation
```html
<div class="card">
  <i class="bi bi-file-earmark-spreadsheet"></i>
  <h3>Your Document Workspace</h3>
  <p>Open the document drafter and a demand letter for Rodriguez v. Mount Sinai is pre-populated with the case facts, medical chronology, and liability analysis. Every statement includes a source citation — click any citation to jump to the exact medical record page or deposition line that supports it.</p>
</div>
```

### Card 9: Analytics Dashboard
```html
<div class="card">
  <i class="bi bi-bar-chart-line"></i>
  <h3>Your Analytics Dashboard</h3>
  <p>Your dashboard shows real-time metrics: 47 active cases, 12 in AI review, 8 with deposition analysis running. The Rodriguez case appears at the top of your priority queue — flagged by the AI as high-value with a strong liability score and an approaching statute of limitations.</p>
</div>
```

---

## D. Case Study Section — Replace "Rodriguez v. Mount Sinai Hospital" Header Lines 366-368

**Current copy:**
> "Featured Case Study · NYC Bar Demo — Rodriguez v. Mount Sinai Hospital — How Veritas Deposition™ exposed a 14-hour treatment gap..."

**Replace with (workspace language):**

```html
<div style="display: inline-block; padding: 8px 16px; background: rgba(201,168,76,0.1); color: var(--gold); border-radius: 100px; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 16px;">
  ⚡ Live from Your Dashboard · Case Detail View
</div>
<h2 class="case-study-h2" style="font-family: 'Playfair Display', serif; font-size: 40px; font-weight: 800; margin-bottom: 8px;">
  Rodriguez <span style="color: var(--gold);">v.</span> Mount Sinai Hospital
</h2>
<p style="color: var(--slate-400); font-size: 18px; max-width: 600px; margin: 0 auto;">
  This is the case open in your workspace right now. Below you can see exactly what the AI surfaced: the Contradiction Detection Engine found 7 inconsistencies between Dr. Miller's deposition testimony and the hospital's own records — and generated cross-examination questions for each one.
</p>
```

---

## E. AI Intake Landing Page — Hero Conversion

**Target:** `ai-legal-intake-software.html` (or `ai-intake-agent.html`)

**Current style:** Marketing description of features.

**Replace hero with:**

```html
<h1>Your AI Intake Agent Is <span>Already Working</span>.</h1>
<p>In your workspace, you can watch the AI intake agent handle an incoming lead in real time. Elena Rodriguez's case was captured, scored at 92/100, and synced to your Clio account — all in under 30 seconds. You can review the transcript, listen to the call recording, and approve the lead with one click. No forms. No callbacks. No missed cases.</p>
```

---

## F. Veritas Deposition Landing Page — Hero Conversion

**Target:** `veritas-deposition.html`

**Current style:** Marketing description of deposition features.

**Replace hero with:**

```html
<h1>Your Deposition <span>Intelligence Dashboard</span> Is Open.</h1>
<p>In your workspace, Dr. Miller's deposition from the Rodriguez case is already analyzed. The Contradiction Detection Engine has cross-referenced all 147 pages of testimony against the evidentiary record and flagged 7 contradictions — including the 14-hour treatment gap. Three impeachment questions are pre-written in your Cross-Examination Builder. You can start preparing for trial right now.</p>
```

---

## G. LexiFlow Strategist™ Landing Page — Hero Conversion

**Target:** `strategist.html`

**Current style:** Marketing description of strategic case advice.

**Replace hero with:**

```html
<h1>Your Case Strategy Is <span>Already Loaded</span>.</h1>
<p>In your Strategist workspace, the Rodriguez case has been evaluated across all 12 liability factors. The AI assigned a Liability Score of 85/100, identified the 14-hour treatment gap as a critical breach of the sepsis protocol standard of care, and estimated a settlement range of $2.8M–$4.2M for New York venue. Three evidentiary weaknesses have been flagged — the AI has already suggested pre-trial motions to address each one.</p>
```

---

## H. Auto-Document Drafter Landing Page — Hero Conversion

**Target:** `auto-document-drafter.html`

**Current style:** Marketing description of document drafting.

**Replace hero with:**

```html
<h1>Your Demand Letter Is <span>Ready for Review</span>.</h1>
<p>In your document workspace, a demand letter for Rodriguez v. Mount Sinai has been drafted automatically. It incorporates the full medical chronology, the 14-hour treatment gap, Dr. Miller's contradicted deposition testimony, and the New York statutory damage framework. Every factual statement links to its source — medical record page, deposition page:line, or discovery exhibit. You can edit, approve, and export to Word in under 60 seconds.</p>
```