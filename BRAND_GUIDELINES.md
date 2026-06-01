# LexiFlow Brand Guidelines

## Brand Overview

**Product Name:** LexiFlow  
**Company:** Ai Future  
**Tagline:** "AI-Powered Legal Intake & Lead Qualification"  
**Domain:** lexiflow.co  

## Logo Variations

| File | Description | Format |
|------|-------------|--------|
| `logo-main.svg` / `.png` | Horizontal wordmark with icon (primary logo) | SVG + PNG |
| `logo-stacked.svg` / `.png` | Vertical/stacked layout (for mobile, social avatars) | SVG + PNG |
| `logo-icon.svg` / `.png` | Icon-only (favicon, app icon, square contexts) | SVG + PNG |
| `logo-monochrome.svg` / `.png` | Light-on-dark variant (dark mode, dark backgrounds) | SVG + PNG |
| `favicon.svg` / `.png` | 32×32 favicon / app icon | SVG + PNG |
| `social-banner.svg` / `.png` | OG image 1200×630px (social sharing, LinkedIn, Twitter) | SVG + PNG |

## Color Palette

### Primary Colors
| Color | Hex | Usage |
|-------|-----|-------|
| LexiFlow Blue | `#2563eb` (blue-600) | Brand accent, CTAs, links, "Flow" wordmark |
| Light Blue | `#3b82f6` (blue-500) | Hover states, gradients |
| Indigo Accent | `#6366f1` (indigo-500) | Secondary gradients, data flow elements |
| Deep Slate | `#0f172a` (slate-900) | Dark background, hero sections |
| Mid Slate | `#1e293b` (slate-800) | Secondary dark backgrounds |
| Slate Base | `#334155` (slate-700) | Body text on light backgrounds |
| Light Slate | `#94a3b8` (slate-400) | Muted text, placeholders |

### Gradient
- **Primary Gradient:** `#2563eb → #6366f1` (Blue to Indigo)
- **Background Gradient:** `#1e293b → #0f172a` (Dark slate for hero)

## Typography

**Primary Font:** Inter (Google Fonts)
- **Weights:** 300 (Light), 400 (Regular), 600 (Semi-Bold), 700 (Bold)
- **Usage:** All UI text, headlines, body copy
- **Fallback:** `'Segoe UI', system-ui, sans-serif`

### Font Sizing
- **Hero Headline:** 3rem–3.75rem (48px–60px)
- **Section Headings:** 1.5rem–2.25rem (24px–36px)
- **Body Text:** 0.875rem–1rem (14px–16px)
- **Small/Meta:** 0.75rem (12px)

## Logo Usage

### Clear Space
- Maintain padding equal to the height of the "L" in "Lexi" on all sides.
- Minimum clear space: 16px on digital, 1/4" on print.

### Minimum Size
- **Horizontal logo:** 140px wide
- **Icon only:** 32px wide
- **Stacked logo:** 100px wide

### Don'ts
- ❌ Do not stretch or distort the logo
- ❌ Do not change the logo colors
- ❌ Do not add drop shadows or effects
- ❌ Do not place on low-contrast backgrounds
- ❌ Do not rearrange the icon and wordmark

## Social Media Assets

### Open Graph Image
- **Dimensions:** 1200×630px
- **File:** `social-banner.png`
- **Description:** Dark background with LexiFlow logo, tagline, feature pills, and URL
- **Usage:** Set as `og:image` and `twitter:image` metatags

## Files to Update in Site

### index.html
Replace the current `bi-briefcase-fill` Bootstrap icon with:
```html
<img src="/branding/logo-main.svg" alt="LexiFlow" height="32" class="h-8">
```

### Favicon
Replace the favicon link:
```html
<link rel="icon" type="image/svg+xml" href="/branding/favicon.svg">
<link rel="icon" type="image/png" href="/branding/favicon.png" sizes="32x32">
```

### OG Image
Update the OG meta tags to point to the new banner:
```html
<meta property="og:image" content="https://lexiflow.co/branding/social-banner.png">
<meta property="twitter:image" content="https://lexiflow.co/branding/social-banner.png">
```
