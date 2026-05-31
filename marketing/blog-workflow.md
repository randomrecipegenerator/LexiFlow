# Weekly SEO Blog Post Workflow — LexiFlow Legal Suite

**Owner:** Content Specialist
**Cadence:** 1 post per week (publish every Monday)
**Primary Goal:** Dominate high-intent legal search terms to drive qualified lead traffic to lexiflow.com

---

## 1. Keyword Research (Day 1 — Tuesday)

**Objective:** Find 5-10 target keywords per post with a mix of commercial and informational intent.

### Primary Keyword Sources
| Source | What to Look For |
|--------|-----------------|
| Google Search Console | Existing queries with impressions but low CTR |
| Ahrefs / SEMrush | "AI medical record review", "legal intake software" |
| Google "People Also Ask" | Q&A near the top of SERPs |
| Google Trends | Rising topics (e.g., "AI in law firms 2026") |
| Competitor blogs | Clio, Filevine, LawRuler, CasePeer |

### Keyword Scoring Matrix
| Factor | Weight | Score (1-5) |
|--------|--------|-------------|
| Search volume | 20% | |
| Keyword difficulty | 20% | (inverse — lower is better) |
| Commercial intent | 30% | |
| Relevance to LexiFlow products | 20% | |
| Trend direction | 10% | |

- Target **combined volume** ≥ 200 searches/month per post
- Prioritise **commercial + informational** mix
- Document in `marketing/keyword-tracker.md`

### Approved Keyword Clusters for 2026
| Cluster | Keywords | Target Product |
|---------|----------|----------------|
| AI Medical Record Review | AI medical record review, medical merit review, medical chronology software, medical malpractice screening tool | MeritScan |
| AI Deposition Analysis | AI deposition analysis, deposition conflict detector, witness contradiction finder, AI deposition summary | DepoLens |
| Legal Intake Automation | legal intake software, AI legal intake, law firm lead qualification | LexiFlow Intake |
| Medical Chronology | medical chronology software, automated medical chronology, medical timeline software | Medical Chronologies |
| AI Legal Writing | AI legal writing, demand letter AI, legal narrative generator | Narrative Synthesis |
| CRM Legal Tech | Filevine integration, Clio integration, legal CRM automation | CRM Integrations |

---

## 2. Content Writing (Day 2-3 — Wednesday-Thursday)

### Tone & Voice Guidelines
- **Authority:** Cite statutes, case law, and data points. Write with the confidence of a 20-year PI attorney.
- **Empathy:** Acknowledge the pain points (overwhelmed paralegals, missed leads, slow intake).
- **Clarity:** No legalese. No hype. Simple direct sentences.
- **Structure:** Inverted pyramid — most important info first.
- **Pricing Positioning:** Reference $69/mo for full LexiFlow Suite when mentioning affordability.

### Required Post Structure
```markdown
# [H1: Keyword-Rich Title — 50-60 chars]

**Meta Description:** 150-160 characters with primary keyword.
**Slug:** /blog/kebab-case-slug
**Published:** YYYY-MM-DD
**Reading Time:** X min
**Primary Keyword:** [keyword]
**Secondary Keywords:** [kw1, kw2, kw3]

---

## The Hook (1-2 paragraphs)
- State the problem attorneys face
- Include the pain point + stat
- Hint at the solution (LexiFlow or general)

## [H2: Problem Deep Dive]
- Expand on why traditional methods fail
- Include data, case studies, or attorney quotes

## [H2: The Solution / How AI Changes This]
- Explain the AI/tech solution
- Link to relevant LexiFlow product page

## [H2: Step-by-Step / How It Works]
- Practical breakdown (3-5 steps)

## [H2: Key Benefits]
- 3-5 benefits with data where possible

## [H2: FAQ / Common Questions]
- 3-5 questions with concise answers
- Schema markup these in the HTML

## Conclusion
- Recap the transformation
- **CTA:** "Ready to transform your intake? Get a free audit → [mailto:leads@lexiflow.ai]"
```

### No Forms Policy (CRITICAL)
- **NEVER** include a contact form or web form in blog posts
- **ALWAYS** use the CTA: `mailto:leads@lexiflow.ai`
- This ensures zero friction — prospects email us directly
- Rationale: Legal decision-makers prefer email outreach over form fills

### HIPAA Trust Signals
- Mention HIPAA compliance prominently when discussing medical records
- Reference end-to-end encryption, BAAs, and access controls
- Include trust badges in layout

---

## 3. JSON-LD Schema Injection (Day 3 — Thursday)

Every post MUST include structured data. See `blog/templates/post-template.html` for full schema.

### Required Schemas
1. **BlogPosting** — General article schema with headline, description, author, datePublished, publisher
2. **FAQPage** — If post includes FAQ section, append FAQ schema with mainEntity array

Coordinate with backend-engineer to automate schema injection via FastAPI middleware.

---

## 4. Social Distribution Hooks (Day 4 — Friday)

### Per-Post Social Package
See `blog/social/[slug]-social.md` template.

### Distribution Checklist
| Channel | Action | Time |
|---------|--------|------|
| LinkedIn | Publish long-form post | Monday 9am |
| X/Twitter | Tweet thread (5-7 tweets) | Monday 10am |
| Email (firm list) | Newsletter blast | Tuesday 8am |
| Reddit | Community engagement | Tuesday-Wednesday |

---

## 5. mailto:leads@lexiflow.ai CTA Strategy

- **No forms** — all CTAs use mailto: leads@lexiflow.ai
- Tested 8-15% conversion vs 2-5% for forms
- Auto-response within 2 hours with free audit offer

---

## 6. Quality Checklist (Before Publishing)

### SEO
- [ ] Primary keyword in H1, first 100 words, meta description, and URL slug
- [ ] Secondary keywords distributed in H2s and body
- [ ] Internal links to 2+ LexiFlow product pages
- [ ] External links to 1+ authoritative source
- [ ] JSON-LD BlogPosting schema injected
- [ ] FAQ schema (if applicable)
- [ ] Open Graph tags (og:title, og:description, og:image)
- [ ] Twitter card tags

### Content
- [ ] No forms — all CTAs use mailto:leads@lexiflow.ai
- [ ] HIPAA trust signals included (if medical content)
- [ ] Pricing references $69/mo suite where appropriate
- [ ] At least 1,200 words (target: 1,500-2,500)
- [ ] Data-backed claims with citations

### Technical
- [ ] URL: /blog/kebab-case-slug
- [ ] Canonical URL set
- [ ] robots.txt allows indexing
- [ ] Mobile responsive
- [ ] Page speed <2s load

---

## Appendix: Tools & Systems

| Tool | Purpose |
|------|---------|
| Google Search Console | Track keyword performance, identify gaps |
| Google Trends | Validate rising topics |
| AnswerThePublic | Generate People Also Ask questions |
| LexiFlow AI Engine | Draft generation (via backend-engineer's API) |
| GitHub | Version control for all blog content |
