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
- Prioritise **commercial + informational** mix (e.g., "AI medical merit review" + "how to screen med mal cases")
- Document in `marketing/keyword-tracker.md`

### Approved Keyword Clusters for 2026
| Cluster | Keywords | Target Product |
|---------|----------|----------------|
| AI Medical Record Review | AI medical record review, medical merit review, medical chronology software, medical malpractice screening tool | MeritScan |
| AI Deposition Analysis | AI deposition analysis, deposition conflict detector, witness contradiction finder, AI deposition summary | DepoLens |
| Legal Intake Automation | legal intake software, AI legal intake, law firm lead qualification, automated intake system | LexiFlow Intake |
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
- Bullet points or numbered list

## [H2: Key Benefits (if applicable)]
- 3-5 benefits with data where possible

## [H2: FAQ / Common Questions]
- 3-5 questions with concise answers
- Schema markup these in the HTML

## Conclusion
- Recap the transformation
- **CTA:** "Ready to transform your intake? Get a free audit → [mailto:leads@lexiflow.ai](mailto:leads@lexiflow.ai)"
```

### No Forms Policy (CRITICAL)
- **NEVER** include a contact form or web form in blog posts
- **ALWAYS** use the CTA: `mailto:leads@lexiflow.ai`
- This ensures zero friction — prospects email us directly
- Rationale: Legal decision-makers prefer email outreach over form fills

### CTA Placement Rules
| Location | CTA Text | Style |
|----------|----------|-------|
| After H2 "Solution" section | "See how LexiFlow handles this →" | Text link to product page |
| Mid-post (after FAQ) | "Want a free medical merit review of a real case? Email us." | mailto link |
| **Conclusion (mandatory)** | "Ready to transform your firm's intake? [Email our team →](mailto:leads@lexiflow.ai)" | Bold button-style link |
| Sidebar/bottom (skyscraper) | "Get a Free Intake Audit → leads@lexiflow.ai" | mailto link |

---

## 3. JSON-LD Schema Injection (Day 3 — Thursday)

Every post MUST include structured data. Template:

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "[Full Post Title]",
  "description": "[Meta Description]",
  "author": {
    "@type": "Organization",
    "name": "LexiFlow Legal Suite",
    "url": "https://lexiflow.com"
  },
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "publisher": {
    "@type": "Organization",
    "name": "LexiFlow",
    "logo": {
      "@type": "ImageObject",
      "url": "https://lexiflow.com/assets/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://lexiflow.com/blog/[slug]"
  },
  "image": {
    "@type": "ImageObject",
    "url": "https://lexiflow.com/blog/images/[slug]-hero.png"
  },
  "keywords": "[primary keyword], [secondary keywords comma separated]",
  "articleSection": "[Content cluster category]",
  "about": {
    "@type": "Thing",
    "name": "[Primary keyword topic]"
  }
}
```

Additionally, if the post has FAQ sections, append FAQ schema:

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question 1?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer 1."
      }
    }
  ]
}
```

### Integration with backend-engineer
- Coordinate with backend-engineer to automate schema injection via FastAPI middleware
- Schema should be server-side rendered into `<script type="application/ld+json">` tags
- Future state: auto-generate from markdown frontmatter

---

## 4. Social Distribution Hooks (Day 4 — Friday)

### Per-Post Social Package
Create in `blog/social/[slug]-social.md`:

```markdown
# Social Distribution: [Post Title]

## LinkedIn (Attorney-Focused)
**Headline (1 line):** [Compelling stat or question, 1 line]
**Body (2-3 paragraphs):**
[Problem → Solution → CTA]
**Link:** https://lexiflow.com/blog/[slug]
**Image:** /blog/images/[slug]-social.png
**Best Time:** Tue-Thu 8-10am or 12-1pm

## X/Twitter (Thread)
1/ [Hook tweet with stat]
2/ [Problem statement]
3/ [Solution highlight]
4/ [Bullet benefits]
5/ CTA: "Read the full post → [link]"

## Email Newsletter (To Firm List)
**Subject Line:** [Intriguing, 40-50 chars]
**Preview:** [Compelling snippet, 100 chars]
**Body:** Brief intro + link to full post + CTA to reply for free audit

## Reddit (r/LawFirm, r/Lawyers)
**Post:** [Question or discussion starter based on post topic]
**Comment:** [Link to blog post only if relevant, no overt selling]
```

### Distribution Checklist
| Channel | Action | Time |
|---------|--------|------|
| LinkedIn | Publish long-form post | Monday 9am |
| X/Twitter | Tweet thread (5-7 tweets) | Monday 10am |
| Email (firm list) | Newsletter blast | Tuesday 8am |
| Reddit | Community engagement | Tuesday-Wednesday |
| Facebook (Legal groups) | Share with discussion prompt | Wednesday |
| Re-share (LinkedIn) | Different angle/quote card | Thursday |

---

## 5. mailto:leads@lexiflow.ai CTA Strategy

### Why mailto: instead of forms
| Factor | Form | mailto: |
|--------|------|---------|
| Friction | High — fields, captcha, submit | Low — one click opens email |
| Trust | Medium — spam concerns | High — personal outreach |
| Conversion rate | 2-5% typical | 8-15% tested |
| Follow-up | Manual export needed | Direct to inbox |
| Mobile UX | Variable | Native email client |

### CTA Variations by Post Type
| Post Type | CTA | Placement |
|-----------|-----|-----------|
| Educational / How-to | "Want a free AI analysis of one of your cases? Email us." | Mid-post + conclusion |
| Product-focused | "See LexiFlow in action. Email our team for a demo." | After feature section |
| Industry trend | "Ready to future-proof your intake? [leads@lexiflow.ai](mailto:leads@lexiflow.ai)" | Conclusion |
| Case study | "Want results like this? Email us for a free audit." | After results section |

### Email Auto-Response Setup
When a prospect emails leads@lexiflow.ai:
1. **Auto-reply (immediate):** "Thanks for reaching out — we'll review your intake process and get back to you within 2 hours."
2. **Human follow-up (within 2 hrs):** Free audit offer with specific recommendations
3. **CRM entry:** Prospect added to pipeline automatically

---

## 6. Quality Checklist (Before Publishing)

### SEO
- [ ] Primary keyword in H1, first 100 words, meta description, and URL slug
- [ ] Secondary keywords distributed in H2s and body
- [ ] Internal links to 2+ LexiFlow product pages
- [ ] External links to 1+ authoritative source (.gov, .edu, known legal publications)
- [ ] Image alt tags with keywords
- [ ] JSON-LD BlogPosting schema injected
- [ ] FAQ schema (if applicable)
- [ ] Open Graph tags (og:title, og:description, og:image)
- [ ] Twitter card tags

### Content
- [ ] No forms — all CTAs use mailto:leads@lexiflow.ai
- [ ] At least 1,200 words (target: 1,500-2,500)
- [ ] Data-backed claims with citations
- [ ] Reading level: Grade 8-10 (not too complex)
- [ ] Scannable: short paragraphs, bullet points, headers
- [ ] Legal accuracy reviewed (no incorrect case law or statutes)

### Technical
- [ ] URL: /blog/kebab-case-slug
- [ ] Canonical URL set
- [ ] robots.txt allows indexing
- [ ] Sitemap updated
- [ ] Page speed checked (target: <2s load)
- [ ] Mobile responsive
- [ ] HTTPS enforced

---

## 7. Blog Post Template Files

See the following template files:
- `blog/templates/post-template.md` — Markdown template for drafting
- `blog/templates/post-template.html` — HTML template with injected schema
- `scripts/generate-blog-post.sh` — Automation script to scaffold new posts

---

## Appendix: Tools & Systems

| Tool | Purpose |
|------|---------|
| Google Search Console | Track keyword performance, identify gaps |
| Google Trends | Validate rising topics |
| AnswerThePublic | Generate People Also Ask questions |
| Grammarly / Hemingway | Proofreading and readability |
| LexiFlow AI Engine | Draft generation (via backend-engineer's API) |
| GitHub | Version control for all blog content |
| Vercel / Railway | Hosting and deployment |
