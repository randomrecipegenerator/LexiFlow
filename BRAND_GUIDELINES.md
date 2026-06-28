# LexiFlow Brand Guidelines — Accuracy Verified (2026-06-28)

## Brand Overview

**Product Name:** LexiFlow Legal Suite  
**Company:** LexiFlow Technologies Inc  
**Tagline:** "Advanced Reasoning AI for the Plaintiff-Side Revolution"  
**Domain:** lexiflow.co  
**Core Principle:** Accuracy First — reliability, traceability, and defensible results are non-negotiable.

## Color Palette

### Primary Colors (Live Site — Verified)
| Color | Hex | CSS Variable | Usage |
|-------|-----|-------------|-------|
| Navy (Primary Brand) | `#0f172a` | `--navy` | Hero sections, dark mode, stats bars, footer — **primary brand color** |
| Navy Light | `#1a3a5c` | `--primary` | Headers, navigation, section backgrounds, feature cards |
| Navy Dark | `#0d1f33` / `#0f1f3a` | `--primary-dark` | Hero gradients, dark backgrounds, CTA sections |
| Gold Accent | `#c9a84c` | `--accent` / `--gold` | All CTAs, highlights, badges, pricing emphasis — **only accent color** |

### Neutral Palette
| Color | Hex | CSS Variable | Usage |
|-------|-----|-------------|-------|
| Slate 50 | `#f8fafc` | `--slate-50` / `--bg-light` | Section alt backgrounds |
| Slate 100 | `#f1f5f9` | `--slate-100` | Card borders, subtle dividers |
| Slate 200 | `#e2e8f0` | `--slate-200` / `--border` | Borders, dividers |
| Slate 400 | `#94a3b8` | `--slate-400` / `--text-muted` | Muted text, metadata |
| Slate 600 | `#475569` | `--slate-600` | Body text |

### Status Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Success Green | `#16a34a` / `#28a745` | Verified status, approved badges |
| Danger Red | `#dc2626` | Contradiction flags, error states |
| Warning Amber | `#f59e0b` | Review-needed status |

### Gradient
- **Hero Gradient:** `#0d1f33 → #1a3a5c` (Primary Dark to Primary Navy)
- **CTA Sections:** `#0d1f33 → #1a3a5c` (matching hero)
- **Gold CTA Buttons:** Solid `#c9a84c` on dark backgrounds

> **⚠️ Do NOT use blue-500/600 or indigo-500.** Those colors were from a previous brand iteration. The live site uses Navy/Gold exclusively.

## Typography

**Primary Font:** Inter (Google Fonts)
- **Weights:** 400 (Regular), 500 (Medium), 600 (Semi-Bold), 700 (Bold), 800 (Extra Bold)
- **Usage:** All UI text, body copy, navigation

**Display Font:** Playfair Display (Google Fonts)
- **Weights:** 600, 700, 800
- **Usage:** Hero headlines (`h1`), section headings (`h2`), feature card titles (`h3`)

### Font Sizing
- **Hero Headline (`h1`):** 2.25rem–3.25rem (36px–52px)
- **Section Headings (`h2`):** 1.5rem–2.25rem (24px–36px)
- **Card Titles (`h3`):** 1.1rem–1.4rem (18px–22px)
- **Body Text:** 0.9375rem–1.0625rem (15px–17px)
- **Small/Meta:** 0.75rem–0.85rem (12px–13px)

## Logo Variations

| File | Description | Format |
|------|-------------|--------|
| `/branding/logo-main.png` | Horizontal wordmark with icon (primary logo) | PNG |
| `/branding/lexiflow-logo-dark.png` | Logo on dark navy background (1536x1024) | PNG |
| `/branding/lexiflow-logo-white.png` | Logo on white background (1536x1024) | PNG |

> Logos are located in `/home/team/shared/LexiFlow-Final/branding/`

## Iconography

- **Primary Icon Set:** Bootstrap Icons (`bi-*`) via CDN
- **Usage:** Feature lists, bullet points, status indicators, CTA enhancements
- **Key Icons:** `bi-check-circle` (verified), `bi-star-fill` (priority), `bi-shield-check` (compliance), `bi-stopwatch` (speed), `bi-translate` (bilingual)

## Badge Styles

### Pricing Badge
- Background: Gold (`#c9a84c`)
- Text: Primary Dark (`#0d1f33`)
- Border-radius: 100px
- Font-size: 0.75rem (12px)
- Font-weight: 700

### Status Badges (Hero/Feature)
- Background: `rgba(255,255,255,0.1)` on dark, `rgba(201,168,76,0.15)` for gold variants
- Border: 1px solid `rgba(255,255,255,0.18)` or `rgba(201,168,76,0.3)`
- Border-radius: 100px
- Font-size: 0.72rem–0.78rem

### Accuracy First Badge
- Background: `rgba(201,168,76,0.15)`
- Border: 1px solid `#c9a84c`
- Text: Gold (`#c9a84c`)
- Content: "✓ Accuracy First"

## Component Styles

### Buttons
| Variant | Background | Text | Hover |
|---------|-----------|------|-------|
| `.btn-primary` | Gold `#c9a84c` | Navy `#0d1f33` | `#d4b85a`, translateY(-1px) |
| `.btn-secondary` | Transparent | White | `rgba(255,255,255,0.08)` |
| `.btn-cta` (nav) | Gold `#c9a84c` | Primary Dark `#0d1f33` | No transform |
| `.btn-outline-light` | Transparent | White, border `rgba(255,255,255,0.3)` | Border gold |

### Cards
- Background: White (`#ffffff`)
- Border: 1px solid `var(--slate-200)` (`#e2e8f0`)
- Border-radius: 12px (`.radius-lg`: 16px for modals)
- Padding: 24px–32px
- Hover: `translateY(-2px)` with `box-shadow`

### Pricing Tiers Display
- Background: `rgba(255,255,255,0.15)` on dark CTA sections
- Border-radius: 8px
- Min-width: 120px
- Tier name: 11px uppercase, font-weight 700
- Tier price: 18px, font-weight 700

## Voice & Tone

- **Primary:** Authoritative, data-driven, senior-attorney level
- **EEAT Signals:** Include author byline with credentials (e.g., "James Delaney, Esq. — Former PI managing partner")
- **CTAs:** "Start Free Trial" (preferred), "Email Our Team" (mailto variant)
- **No Forms Policy:** All CTAs use `mailto:leads@lexiflow.co` — never embed HTML forms
- **HIPAA:** Always include 🔒 HIPAA Compliant badge when medical data is discussed
- **Pricing:** Always reference as "$29/month for Starter, $99/month for Professional, or $129/month for Enterprise"

## Assets Directory

All brand and UI assets are located at:
`/home/team/shared/LexiFlow-Final/branding/`

See `ASSET_INDEX.md` for the full directory structure.

---

*Last updated: June 28, 2026 — Verified against live site at lexiflow.co*
*For questions, contact the team lead.*