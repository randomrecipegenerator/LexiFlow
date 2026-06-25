# Expanded SEO Audit — All Primary Landing Pages (June 25, 2026)

## Executive Summary

Following the homepage SEO audit (see `seo/seo_homepage_audit_report.md`), this expanded audit examines the SEO readiness of all high-priority landing pages. The findings reveal **inconsistent meta hygiene** across pages — while each has a unique title and description, critical elements like OG/Twitter tags, JSON-LD, and canonical URLs are **sporadically missing**. Many pages also use **copy-pasted meta keywords** that don't reflect the specific page content.

---

## Page-by-Page Findings

### 1. ai-legal-intake-software.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ✅ | "AI Legal Intake Software for Law Firms | LexiFlow" — good, targets primary keyword |
| Meta description | ✅ | Mentions "Reasoning AI", "enterprise-grade" — good |
| Meta keywords | ❌ | Missing entirely |
| Canonical URL | ✅ | `https://lexiflow.co/ai-legal-intake-software` |
| OG Tags | ❌ | Missing |
| Twitter Card | ❌ | Missing |
| JSON-LD | ❌ | Missing |
| H1 | ✅ | Present, good hierarchy |

**Priority**: HIGH — this is a primary SEO landing page for "AI legal intake software" keyword

---

### 2. veritas-deposition.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ✅ | "Legal Transcript Analysis & Deposition AI Software | Veritas Deposition™" |
| Meta description | ✅ | Mentions "Evidence Intelligence System", "Contradiction Detection Engine" |
| Meta keywords | ❌ | Missing |
| Canonical URL | ✅ | `https://lexiflow.co/veritas-deposition` |
| OG Tags | ❌ | Missing |
| Twitter Card | ❌ | Missing |
| JSON-LD | ❌ | Missing |
| H1 | ✅ | Present |

**Priority**: HIGH — Veritas Deposition™ is the flagship product

---

### 3. auto-document-drafter.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ✅ | "Auto-Document Drafter | LexiFlow Technologies Inc" — could be stronger ("Demand Letter Software") |
| Meta description | ✅ | Good — mentions "demand letters", "pleadings", "settlement brochures" |
| Meta keywords | ❌ | Missing |
| Canonical URL | ❌ | Missing |
| OG Tags | ❌ | Missing |
| Twitter Card | ❌ | Missing |
| JSON-LD | ❌ | Missing |
| H1 | ✅ | Present |

**Priority**: HIGH — high-intent transactional page

---

### 4. strategist.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ⚠️ | Could not read file (unexpected format/access issue) |
| Meta description | ⚠️ | Needs verification |
| OG/Twitter/JSON-LD | ⚠️ | Needs verification |

**Action**: Investigate file integrity. File is ~26KB but ReadFile/GrepTool return no matches for standard HTML tags.

---

### 5. solutions.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ✅ | "Enterprise AI Solutions | LexiFlow" — generic, could target "legal operations software" |
| Meta description | ❌ | Missing entirely |
| Meta keywords | ✅ | Present (copy-pasted generic list) |
| Canonical URL | ❌ | Missing |
| OG Tags | ⚠️ | Partial — has `og:title`, `og:description`, `og:image` but missing `og:url`, `og:type`, `og:site_name` |
| Twitter Card | ⚠️ | Has `twitter:card` and `twitter:image` but missing `twitter:title`, `twitter:description` |
| JSON-LD | ❌ | Missing |

**Priority**: HIGH — this is the main "Workspace" solutions page

---

### 6. personal-injury-software.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ✅ | "Personal Injury Software — AI-Powered Intake & Case Management | LexiFlow" |
| Meta description | ✅ | Targets "medical chronology software", "law firm intake software" — but first sentence should be about PI software |
| Meta keywords | ✅ | Present (copy-pasted generic list from solutions.html) |
| Canonical URL | ❌ | Missing |
| OG Tags | ❌ | Missing |
| Twitter Card | ❌ | Missing |
| JSON-LD | ❌ | Missing |

**Priority**: HIGH — primary PI software landing page

---

### 7. ai-medical-chronologies.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ✅ | "Medical AI Chronologies | Enterprise Litigation Intelligence" |
| Meta description | ✅ | Good — mentions "AI medical chronology software", "thousands of pages" |
| Canonical URL | ⚠️ | Present but has `.html` extension: `/ai-medical-chronologies.html` — should be clean URL |
| OG Tags | ❌ | Missing |
| Twitter Card | ❌ | Missing |
| JSON-LD | ❌ | Missing |

---

### 8. voice-ai-receptionist.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ✅ | "Voice AI Receptionist — LexiFlow" |
| Meta description | ✅ | Good — mentions "high-volume receptionist" but first sentence is a copy-paste generic |
| Meta keywords | ✅ | Present (same copy-pasted list) |
| Canonical URL | ❌ | Missing |
| OG Tags | ❌ | Missing |
| Twitter Card | ❌ | Missing |
| JSON-LD | ✅ | Product schema with price — good, but `@graph` wrapper structure could be simplified |

---

### 9. meritscan.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ✅ | "Medical Malpractice & Surgical Error Case Screening AI | MeritScan" |
| Meta description | ✅ | Good — targets "surgical error", "medical merit" keywords |
| Canonical URL | ❌ | Missing |
| OG Tags | ❌ | Missing |
| Twitter Card | ❌ | Missing |
| JSON-LD | ❌ | Missing |

---

### 10. pricing.html
| Element | Status | Notes |
|---------|--------|-------|
| Title | ✅ | "LexiFlow Pricing — $29/mo Starter | $129/mo Enterprise" |
| Meta description | ✅ | Good — includes pricing, product names |
| Meta keywords | ✅ | Present (copy-pasted generic) |
| Canonical URL | ❌ | Missing |
| OG Tags | ❌ | Missing |
| Twitter Card | ❌ | Missing |
| JSON-LD | ✅ | Product schema with AggregateOffer — good |

---

## Critical Cross-Cutting Issues

### Issue 1: OG & Twitter Cards Missing on 8/10 Pages
Only `solutions.html` has partial OG/Twitter tags. Every other page lacks these entirely.
**Impact**: Links shared on LinkedIn, Facebook, X/Twitter, Slack render as bare URLs

### Issue 2: JSON-LD Present on Only 2/10 Pages
Only `voice-ai-receptionist.html` and `pricing.html` have structured data.
**Impact**: No rich results for most pages in Google SERPs

### Issue 3: Canonical URLs Missing on 6/10 Pages
Missing on: auto-document-drafter, solutions, personal-injury-software, voice-ai-receptionist, meritscan, pricing
**Risk**: Duplicate content issues if pages are accessed via multiple URLs

### Issue 4: Copy-Pasted Meta Keywords
`solutions.html`, `personal-injury-software.html`, `voice-ai-receptionist.html`, and `pricing.html` all use the **exact same** meta keywords string: "medical chronology software, law firm intake software, AI medical record review, personal injury law firm software..." — regardless of actual page content. This is poor SEO practice.

### Issue 5: Generic/Non-SEO Titles
Some titles are too generic (e.g., "Enterprise AI Solutions | LexiFlow") and don't include the primary keyword the page should rank for.

---

## Priority Implementation Plan

### Wave 1 — Immediate Fix (High-Impact Pages)
| Page | Fix | Effort |
|------|-----|--------|
| `ai-legal-intake-software.html` | Add OG, Twitter, JSON-LD (SoftwareApplication + Organization) | Medium |
| `veritas-deposition.html` | Add OG, Twitter, JSON-LD (Product + Organization) | Medium |
| `auto-document-drafter.html` | Add canonical, OG, Twitter, JSON-LD | Medium |
| `solutions.html` | Add meta description, fix OG, fix Twitter, add JSON-LD, add canonical | Medium |

### Wave 2 — Secondary Pages
| Page | Fix | Effort |
|------|-----|--------|
| `personal-injury-software.html` | Add canonical, OG, Twitter, JSON-LD | Medium |
| `ai-medical-chronologies.html` | Fix canonical (remove .html), add OG, Twitter, JSON-LD | Low |
| `meritscan.html` | Add canonical, OG, Twitter, JSON-LD | Medium |
| `voice-ai-receptionist.html` | Add canonical, OG, Twitter, fix meta description | Low |

### Wave 3 — Cleanup & Templates
- Standardize meta keywords to be page-specific (not copy-pasted)
- Create site-wide OG/Twitter/JSON-LD template pattern for all future pages
- Investigate strategist.html file integrity

---

## Recommended Template Pattern

For consistency, every page should include this standard `<head>` block:

```html
<!-- Primary Meta -->
<title>[Page-Specific Title] | LexiFlow</title>
<meta name="description" content="[Page-specific, 155-160 chars, targets primary keyword]" />
<link rel="canonical" href="https://lexiflow.co/[page-path]" />

<!-- Open Graph -->
<meta property="og:title" content="[Page Title - same as <title>]" />
<meta property="og:description" content="[Description - same as meta description]" />
<meta property="og:url" content="https://lexiflow.co/[page-path]" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="LexiFlow Technologies Inc" />
<meta property="og:image" content="https://lexiflow.co/social-banner.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="[Same as og:title]" />
<meta name="twitter:description" content="[Same as og:description]" />
<meta name="twitter:image" content="https://lexiflow.co/social-banner.png" />

<!-- JSON-LD: Organization + BreadcrumbList (site-wide) + Page-specific Product/SoftwareApplication -->
```

---

## Homepage Index.html — Verification

The homepage (`index.html`) was already fixed in the previous task (branch `feat/seo-homepage-audit`). It now has:
- ✅ OG & Twitter Card meta tags
- ✅ 5 JSON-LD blocks (Organization, WebSite, SoftwareApplication, BreadcrumbList, FAQPage)
- ✅ Fixed heading hierarchy (H1→H2→H3→H4)
- ✅ SEO-optimized title/description with target keywords
- ✅ Updated robots.txt and sitemap.xml (138 URLs)

The homepage's changes should be **merged to main** before applying this expanded audit's fixes, so the new pages follow the same pattern.

---

## Target Keyword + Active Workspace Balance

Per the lead's guidance, we need to balance "Agentic Browsing" / "Active Workspace" conversion language with SEO keywords:

| Page | SEO Keyword Priority | Active Workspace Angle |
|------|---------------------|----------------------|
| index.html | "Legal Operations Software", "Legal Matter Management" | ✅ Already balanced: H1 = "AI Legal Operations & Active Case Workspace" |
| solutions.html | "Legal Operations Software" | Rename title from "Enterprise AI Solutions" to "Legal Operations Software & Active Workspace" |
| ai-legal-intake-software.html | "AI Legal Intake Software" | ✅ Good as-is — product-focused page |
| veritas-deposition.html | "Deposition Analysis AI" | ✅ Good as-is — product-focused page |
| auto-document-drafter.html | "Demand Letter Software" | Could add "Live Document Workspace" sub-header |

**Recommendation**: Reserve the full "Active Workspace" branding for the index.html and solutions.html. Keep product pages focused on their core keyword (e.g., "AI Legal Intake Software", "Deposition Analysis AI") since these are what buyers search for.