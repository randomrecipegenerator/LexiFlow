# MeritScan & DepoLens — Landing Page Copy Briefs

Quick-reference copy outlines for developers and the designer to build high-conversion landing pages for each product. Full strategy details in `marketing/meritscan-depolens-seo-strategy.md`.

---

## MeritScan Landing Page

**URL:** `/meritscan`  
**Title Tag:** MeritScan — AI Medical Merit Review for Attorneys | Screen Cases in Minutes  
**Meta Desc:** Upload medical records. Get a citation-backed preliminary merit report with chronology, negligence markers, and standard of care analysis — in minutes.  
**Primary KWs:** AI medical record review, medical merit review, medical malpractice screening tool  

### Sections
1. **Hero** — Screen MedMal Cases in Minutes, Not Weeks. CTA: "Start Free Screening"
2. **Problem** — Paralegals drowning in records (8-12 hrs/case manual vs 3 min AI)
3. **Features** — Chronology, Negligence Markers, Standard of Care Check, Citation Report, $75/case, Export
4. **How It Works** — 3 steps: Upload → AI Analyzes → Get Report
5. **Pricing** — Free (5 uploads), $75/case (full merit), Enterprise (custom)
6. **FAQ** — Schema markup (accuracy, file types, pricing)
7. **CTA** — "Get Started Free — No Credit Card Required"

---

## DepoLens Landing Page

**URL:** `/depolens`  
**Title Tag:** DepoLens — AI Deposition Conflict Detector | Find Witness Contradictions Instantly  
**Meta Desc:** Upload deposition transcripts. AI detects contradictions between witnesses, builds a unified fact chronology, and generates executive summaries. Essential for trial prep.  
**Primary KWs:** AI deposition analysis, deposition conflict detector, witness contradiction finder  

### Sections
1. **Hero** — Find Every Deposition Contradiction — In Seconds. CTA: "Analyze a Transcript Free"
2. **Problem** — Manual review misses 30%+ contradictions, takes hours per transcript pair
3. **Features** — Conflict Detection, Fact Chronology, Executive Summary, Admissions, Risks, Multi-Witness
4. **How It Works** — 3 steps: Upload → AI Cross-References → Get Analysis
5. **Pricing** — $99/transcript, $79/transcript (10+), Enterprise (custom)
6. **FAQ** — Schema markup (file formats, multi-witness, AI vs human)
7. **CTA** — "Upload a Transcript Free"

---

## SEO Tags (for all product pages)

### Open Graph
```html
<meta property="og:type" content="website">
<meta property="og:url" content="https://lexiflow.co/[product]">
<meta property="og:title" content="[Title Tag]">
<meta property="og:description" content="[Meta Description]">
```

### Schema
```json
{"@context":"https://schema.org","@type":"SoftwareApplication","name":"[Product Name]","operatingSystem":"Web","applicationCategory":"Legal Software","offers":{"@type":"Offer","price":"[Price]","priceCurrency":"USD"}}
```

### FAQ Schema (10-15 Q&A pairs)
Use self-referencing FAQ schema with `mainEntity` array — 8-12 questions covering pricing, file formats, accuracy, use cases.
