# Marketplace Marketing Assets — cto.new Listing

**Location:** `/home/team/shared/branding/marketplace-assets/`

Created for LexiFlow's marketplace listing on cto.new to attract early adopters and investors.

## Asset Inventory

| # | File | Format | Dimensions | Purpose |
|---|------|--------|-----------|---------|
| 1 | `marketplace-cover.svg` | SVG | 1920×1080 (16:9) | Hero banner — combines empathy + AI intelligence, shows dashboard mockup with stats |
| 2 | `listing-icon.svg` | SVG | 512×512 (square) | Marketplace listing icon — LexiFlow scales-of-justice logo on dark slate |
| 3 | `promo-24-7.svg` | SVG | 1200×630 (1.91:1) | Promo graphic — "24/7 AI Receptionist + Smart Email Intake" headline |
| 4 | `screenshot-lead-qualification.svg` | SVG | 800×600 | Feature screenshot — Lead qualification donut chart + score bars |
| 5 | `screenshot-front-desk.svg` | SVG | 800×600 | Feature screenshot — AI Front Desk settings (Voice + Email panels) |
| 6 | `screenshot-lead-detail.svg` | SVG | 800×600 | Feature screenshot — Lead detail view with AI Summary |

## Design System

**Colors**: Dark slate (`#0f172a` → `#1e293b`) backgrounds, blue-gradient (`#2563eb` → `#6366f1`) accents, green (`#16a34a`) for success states, amber (`#d97706`) for warnings.

**Typography**: Inter (system-ui fallback), 300-800 weights.

**Devices Shown**: Dashboard mockups with dark theme consistent with LexiFlow's actual UI.

## Usage Notes

- All assets are SVG — scalable to any size, crisp on retina displays.
- To upload to cto.new, you may need to convert to PNG. Use:
  ```bash
  source /home/team/shared/lexiflow-mvp/venv/bin/activate
  python3 -c "import cairosvg; cairosvg.svg2png(url='FILE.svg', write_to='FILE.png', output_width=W, output_height=H)"
  ```
- The cover image (16:9) works best as the primary marketplace listing image.
- Feature screenshots can be used in the description body or as secondary images.
- The promo graphic is optimized for social sharing / Twitter cards.

## Suggested Listing Copy

**Headline**: The AI Front Desk for Law Firms — 24/7 Voice & Email Intake
**Tagline**: Capture, qualify, and convert leads with Reasoning AI. Never miss a case.
**Description**: LexiFlow transforms law firm intake from a manual, leaky bucket into a 24/7 high-conversion revenue engine. Uses Reasoning AI to qualify leads with the nuance of a senior attorney.
