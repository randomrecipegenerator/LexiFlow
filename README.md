# Demo-Specific Branding Assets

This directory contains extracted branding assets for two law firm demo partners.

## Clifford Law Offices

- **Website:** [cliffordlaw.com](https://www.cliffordlaw.com)
- **Directory:** `clifford-law-assets/`
- **Logos:**
  - `clifford-law-logo.svg` — Green logo (primary, SVG)
  - `clifford-law-logo-white.svg` — White logo variant (for dark backgrounds, SVG)
- **Brand Colors:**
  | Role | Hex | Sample |
  |------|-----|--------|
  | Primary | `#005941` | ████ Dark Green |
  | Primary Light | `#008964` | ████ Medium Green |
  | Secondary | `#c57a55` | ████ Terracotta |
  | Accent | `#cb6942` | ████ Warm Orange |
  | Light Accent | `#8cd8c1` | ████ Mint |
  | Dark | `#22262B` | ████ Near Black |
- **Config:** `branding-config.json` — Ready for database injection.

## Smith LaCien LLP

- **Website:** [smithlacien.com](https://www.smithlacien.com)
- **Directory:** `smith-lacien-assets/`
- **Logos:**
  - `smith-lacien-logo.svg` — Primary logo (SVG)
- **Brand Colors:**
  | Role | Hex | Sample |
  |------|-----|--------|
  | Primary | `#0A4030` | ████ Dark Forest Green |
  | Primary Dark | `#001D0B` | ████ Very Dark Green |
  | Secondary | `#006ba1` | ████ Blue |
  | Secondary Light | `#0693e3` | ████ Sky Blue |
  | Accent | `#004a59` | ████ Teal |
  | Highlight | `#00d084` | ████ Bright Green |
  | Dark | `#313131` | ████ Charcoal |
- **Config:** `branding-config.json` — Ready for database injection.

## Usage

### For the AI Software Engineer

The `branding-config.json` files map directly to the `Firm` model's expected fields (`branding_colors` and `branding_logo`). The engineer can:

1. Read the JSON file for the target firm.
2. Map the fields: `branding_logo` → URL path to the SVG, `branding_colors` → the colors object.
3. Provision demo accounts with these values for instant branded demos.

### Notes

- All logos are vector SVG — scalable and high-resolution.
- Colors were extracted from each firm's live website by analyzing CSS and inline styles.
- Both firms have a professional legal aesthetic compatible with LexiFlow's existing design framework.

## Quick Start (Database Initialization)
To initialize the LexiFlow database schema:
```bash
python create_tables.py
```
Refer to [DEPLOYMENT.md](DEPLOYMENT.md) for full production deployment instructions.
