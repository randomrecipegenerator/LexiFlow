# LexiFlow Asset Index — Form-Free & Accuracy Verified (2026-06-28)

## Brand Colors (Live Site — Verified)

| Name | Hex | CSS Variable | Primary Usage |
|------|-----|-------------|---------------|
| Navy | `#0f172a` | `--navy` | Hero backgrounds, dark sections, stats bars |
| Navy Light | `#1a3a5c` | `--primary` | Navigation, section headers, card headings |
| Navy Dark | `#0d1f33` / `#0f1f3a` | `--primary-dark` | Hero gradients, footer, CTA backgrounds |
| Gold | `#c9a84c` | `--accent` / `--gold` | All CTAs, badges, highlights, pricing emphasis |

> ⚠️ **No other brand colors are currently in use.** Previous iterations used Teal (`#0D9488`), Blue-600 (`#2563eb`), and Indigo-500 (`#6366f1`) — these are **deprecated** and must not appear anywhere. The live site is Navy + Gold exclusively.

See `BRAND_GUIDELINES.md` for the full neutral palette (slate tones), status colors, typography, and component style specifications.

---

## Directory Structure (Current Assets)

```
branding/
├── BRAND_GUIDELINES.md
└── assets/
    ├── lexiflow-logo-dark.png
    ├── lexiflow-logo-white.png
    ├── slides/
    │   └── [12 sales slides — see full listing in earlier version]
    ├── mockups/
    │   ├── narrative-synthesis.png
    │   ├── lead-analytics-dashboard.png
    │   └── intake-chatbot-widget.png
    └── report/
        └── roi-report-template.html
```

---

## Assets That Do NOT Exist Yet

The following have been referenced in older documentation but **do not exist** in the filesystem and must not be linked or promoted:

- ❌ `downloads/lexiflow-medical-chronology-template.pdf`
- ❌ `downloads/lexiflow-medical-chronology-sample.pdf`
- ❌ `downloads/lexiflow-record-review-checklist.pdf`
- ❌ `downloads/florida-medmal-ai-intake.pdf` through `illinois-medmal-ai-intake.pdf`
- ❌ Any "Demand Letter Pack" or "Demand Letter Template" resources

Before adding any of these to the asset index or linking them from the site, the actual PDF files must be created and saved to `/home/team/shared/LexiFlow-Final/downloads/`. Until then, all references to them should be treated as dead links and removed.

---

## Active Case Study

| Case | File | Description |
|------|------|-------------|
| Rodriguez v. Mount Sinai | `/case-studies/rodriguez-v-mount-sinai.html` | Delayed sepsis → bilateral amputation; Contradiction Detection Engine™ demo; $4.2M NY value |

---

## Form-Free Compliance (Revision 68)

In accordance with the Form-Free mandate:
- All CTAs use **`mailto:leads@lexiflow.co`** — no embedded HTML forms anywhere
- No lead capture modals, email-gated downloads, or contact forms
- The 30-day free trial signup at `/signup` is the only conversion path
- This asset index references no downloadable gated content

---

## Demo Credentials

- **Dashboard:** https://lexiflow.co/dashboard.html
- **Attorney:** attorney@lexiflow.tech / TestPass123!
- **Firm Slug:** lexiflow-tech
- **Demo Case:** Rodriguez v. Mount Sinai

---

*Last updated: June 28, 2026 — Verified against live site at lexiflow.co*
*Form-Free compliant per Revision 68. Brand colors verified against live CSS.*